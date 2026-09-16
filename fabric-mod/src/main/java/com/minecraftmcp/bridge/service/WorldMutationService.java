package com.minecraftmcp.bridge.service;

import com.google.gson.JsonObject;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

public class WorldMutationService {
    private static WorldMutationService INSTANCE;

    public static synchronized WorldMutationService getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new WorldMutationService();
        }
        return INSTANCE;
    }

    private WorldMutationService() {}

    public BlockState parseBlockState(String blockStateStr) {
        if (blockStateStr == null || blockStateStr.isBlank()) {
            throw new IllegalArgumentException("Block state string cannot be empty");
        }
        try {
            return BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK, blockStateStr, true).blockState();
        } catch (Exception e) {
            Identifier id = Identifier.tryParse(blockStateStr);
            if (id != null && BuiltInRegistries.BLOCK.containsKey(id)) {
                return BuiltInRegistries.BLOCK.getValue(id).defaultBlockState();
            }
            throw new IllegalArgumentException("Unknown or invalid block state: " + blockStateStr, e);
        }
    }

    private void ensureLoaded(ServerLevel level, BlockPos pos) {
        if (!level.isLoaded(pos)) {
            level.getChunk(pos.getX() >> 4, pos.getZ() >> 4, net.minecraft.world.level.chunk.status.ChunkStatus.FULL, true);
        }
    }

    public JsonObject setBlock(ServerLevel level, BlockPos pos, String blockStateStr, int flags) {
        ensureLoaded(level, pos);

        BlockState previousState = level.getBlockState(pos);
        BlockState targetState = parseBlockState(blockStateStr);

        int updateFlags = flags > 0 ? flags : 11; // 11 = Block.UPDATE_ALL_IMMEDIATE (UPDATE_NEIGHBORS | UPDATE_CLIENTS | UPDATE_IMMEDIATE)
        boolean placed = level.setBlock(pos, targetState, updateFlags);

        BlockState currentState = level.getBlockState(pos);
        boolean verified = currentState.is(targetState.getBlock());
        boolean success = placed || verified;

        JsonObject data = new JsonObject();
        data.addProperty("action", "place_block");

        JsonObject posObj = new JsonObject();
        posObj.addProperty("x", pos.getX());
        posObj.addProperty("y", pos.getY());
        posObj.addProperty("z", pos.getZ());
        data.add("position", posObj);

        data.addProperty("block", BlockStateParser.serialize(targetState));
        data.addProperty("previous_block", BlockStateParser.serialize(previousState));
        data.addProperty("placed", success);
        data.addProperty("verified", verified);

        return data;
    }

    public JsonObject breakBlock(ServerLevel level, BlockPos pos, boolean dropLoot, ServerPlayer player) {
        ensureLoaded(level, pos);

        BlockState previousState = level.getBlockState(pos);
        if (previousState.isAir()) {
            JsonObject data = new JsonObject();
            data.addProperty("action", "break_block");

            JsonObject posObj = new JsonObject();
            posObj.addProperty("x", pos.getX());
            posObj.addProperty("y", pos.getY());
            posObj.addProperty("z", pos.getZ());
            data.add("position", posObj);

            data.addProperty("previous_block", "minecraft:air");
            data.addProperty("current_block", "minecraft:air");
            data.addProperty("verified", true);
            data.addProperty("dropped_items", false);
            return data;
        }

        boolean destroyed = level.destroyBlock(pos, dropLoot, player);
        BlockState currentState = level.getBlockState(pos);
        boolean verified = currentState.isAir();

        JsonObject data = new JsonObject();
        data.addProperty("action", "break_block");

        JsonObject posObj = new JsonObject();
        posObj.addProperty("x", pos.getX());
        posObj.addProperty("y", pos.getY());
        posObj.addProperty("z", pos.getZ());
        data.add("position", posObj);

        data.addProperty("previous_block", BlockStateParser.serialize(previousState));
        data.addProperty("current_block", BlockStateParser.serialize(currentState));
        data.addProperty("destroyed", destroyed);
        data.addProperty("verified", verified);
        data.addProperty("dropped_items", dropLoot);

        return data;
    }

    public JsonObject fillRegion(ServerLevel level, BlockPos from, BlockPos to, String blockStateStr, String replaceFilter) {
        int minX = Math.min(from.getX(), to.getX());
        int maxX = Math.max(from.getX(), to.getX());
        int minY = Math.min(from.getY(), to.getY());
        int maxY = Math.max(from.getY(), to.getY());
        int minZ = Math.min(from.getZ(), to.getZ());
        int maxZ = Math.max(from.getZ(), to.getZ());

        long volume = (long) (maxX - minX + 1) * (maxY - minY + 1) * (maxZ - minZ + 1);
        if (volume > 500) {
            throw new IllegalArgumentException("Fill volume (" + volume + ") exceeds maximum safety limit (500 blocks)");
        }

        BlockState targetState = parseBlockState(blockStateStr);
        BlockState filterState = (replaceFilter != null && !replaceFilter.isBlank()) ? parseBlockState(replaceFilter) : null;

        int placedCount = 0;
        int failedCount = 0;

        for (BlockPos p : BlockPos.betweenClosed(minX, minY, minZ, maxX, maxY, maxZ)) {
            ensureLoaded(level, p);
            if (filterState != null) {
                BlockState current = level.getBlockState(p);
                if (!current.is(filterState.getBlock())) {
                    continue;
                }
            }
            boolean ok = level.setBlock(p, targetState, 11);
            if (ok || level.getBlockState(p).is(targetState.getBlock())) {
                placedCount++;
            } else {
                failedCount++;
            }
        }

        // Closed-loop sample verification at 8 corners + center
        boolean verified = true;
        BlockPos[] samplePoints = new BlockPos[]{
                new BlockPos(minX, minY, minZ),
                new BlockPos(maxX, minY, minZ),
                new BlockPos(minX, maxY, minZ),
                new BlockPos(maxX, maxY, minZ),
                new BlockPos(minX, minY, maxZ),
                new BlockPos(maxX, minY, maxZ),
                new BlockPos(minX, maxY, maxZ),
                new BlockPos(maxX, maxY, maxZ),
                new BlockPos((minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2)
        };

        for (BlockPos sample : samplePoints) {
            if (level.isLoaded(sample)) {
                if (filterState != null) {
                    // if filtered, only check if placed
                    continue;
                }
                if (!level.getBlockState(sample).is(targetState.getBlock())) {
                    verified = false;
                    break;
                }
            }
        }

        JsonObject data = new JsonObject();
        data.addProperty("action", "fill_region");

        JsonObject fromObj = new JsonObject();
        fromObj.addProperty("x", from.getX());
        fromObj.addProperty("y", from.getY());
        fromObj.addProperty("z", from.getZ());
        data.add("from", fromObj);

        JsonObject toObj = new JsonObject();
        toObj.addProperty("x", to.getX());
        toObj.addProperty("y", to.getY());
        toObj.addProperty("z", to.getZ());
        data.add("to", toObj);

        data.addProperty("block", BlockStateParser.serialize(targetState));
        data.addProperty("volume", volume);
        data.addProperty("placed_count", placedCount);
        data.addProperty("failed_count", failedCount);
        data.addProperty("verified", verified);

        return data;
    }

    public JsonObject interactWithBlock(ServerLevel level, ServerPlayer player, BlockPos pos, InteractionHand hand) {
        ensureLoaded(level, pos);

        BlockState beforeState = level.getBlockState(pos);
        InteractionHand useHand = (hand != null) ? hand : InteractionHand.MAIN_HAND;
        BlockHitResult hitResult = new BlockHitResult(Vec3.atCenterOf(pos), Direction.UP, pos, false);
        ItemStack heldItem = player.getItemInHand(useHand);

        InteractionResult result = player.gameMode.useItemOn(player, level, heldItem, useHand, hitResult);
        BlockState afterState = level.getBlockState(pos);
        boolean stateChanged = !beforeState.equals(afterState);

        String blockKey = BuiltInRegistries.BLOCK.getKey(afterState.getBlock()).toString();
        String interactionType = "generic_interaction";
        if (blockKey.contains("door") || blockKey.contains("trapdoor") || blockKey.contains("gate")) {
            interactionType = "door_toggle";
        } else if (blockKey.contains("button")) {
            interactionType = "button_press";
        } else if (blockKey.contains("lever")) {
            interactionType = "lever_toggle";
        } else if (blockKey.contains("chest") || blockKey.contains("barrel") || blockKey.contains("shulker")) {
            interactionType = "container_open";
        } else if (blockKey.contains("crafting_table")) {
            interactionType = "crafting_table_open";
        } else if (blockKey.contains("furnace") || blockKey.contains("smoker") || blockKey.contains("blast_furnace")) {
            interactionType = "furnace_open";
        }

        JsonObject data = new JsonObject();
        data.addProperty("action", "interact_with_block");

        JsonObject posObj = new JsonObject();
        posObj.addProperty("x", pos.getX());
        posObj.addProperty("y", pos.getY());
        posObj.addProperty("z", pos.getZ());
        data.add("position", posObj);

        data.addProperty("target_block", BlockStateParser.serialize(afterState));
        data.addProperty("interaction_type", interactionType);
        data.addProperty("state_changed", stateChanged);
        data.addProperty("verified", result.consumesAction() || stateChanged);

        return data;
    }
}
