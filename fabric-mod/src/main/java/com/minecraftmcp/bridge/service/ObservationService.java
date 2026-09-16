package com.minecraftmcp.bridge.service;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

import java.util.List;
import java.util.UUID;

public class ObservationService {
    private static ObservationService INSTANCE;

    public static synchronized ObservationService getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new ObservationService();
        }
        return INSTANCE;
    }

    private ObservationService() {}

    public ServerPlayer resolvePlayer(MinecraftServer server, String nameOrUuid) {
        if (server == null || server.getPlayerList() == null) {
            return null;
        }
        if (nameOrUuid == null || nameOrUuid.isBlank()) {
            List<ServerPlayer> players = server.getPlayerList().getPlayers();
            return players.isEmpty() ? null : players.get(0);
        }
        ServerPlayer player = server.getPlayerList().getPlayerByName(nameOrUuid);
        if (player != null) {
            return player;
        }
        try {
            UUID uuid = UUID.fromString(nameOrUuid);
            return server.getPlayerList().getPlayer(uuid);
        } catch (IllegalArgumentException ignored) {
            return null;
        }
    }

    public JsonObject getPlayerStatus(ServerPlayer player) {
        JsonObject obj = new JsonObject();
        obj.addProperty("uuid", player.getStringUUID());
        obj.addProperty("name", player.getName().getString());

        JsonObject pos = new JsonObject();
        pos.addProperty("x", player.getX());
        pos.addProperty("y", player.getY());
        pos.addProperty("z", player.getZ());
        obj.add("position", pos);

        BlockPos bp = player.blockPosition();
        JsonObject blockPos = new JsonObject();
        blockPos.addProperty("x", bp.getX());
        blockPos.addProperty("y", bp.getY());
        blockPos.addProperty("z", bp.getZ());
        obj.add("blockPosition", blockPos);

        JsonObject rot = new JsonObject();
        rot.addProperty("yaw", player.getYRot());
        rot.addProperty("pitch", player.getXRot());
        rot.addProperty("headYaw", player.getYHeadRot());
        obj.add("rotation", rot);

        obj.addProperty("health", player.getHealth());
        obj.addProperty("maxHealth", player.getMaxHealth());
        obj.addProperty("food", player.getFoodData().getFoodLevel());
        obj.addProperty("saturation", player.getFoodData().getSaturationLevel());
        obj.addProperty("gameMode", player.gameMode().getName());
        obj.addProperty("dimension", player.level().dimension().identifier().toString());
        obj.addProperty("selectedSlot", player.getInventory().getSelectedSlot());

        ItemStack mainHand = player.getMainHandItem();
        if (!mainHand.isEmpty()) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("id", BuiltInRegistries.ITEM.getKey(mainHand.getItem()).toString());
            itemObj.addProperty("count", mainHand.getCount());
            obj.add("heldItem", itemObj);
        } else {
            obj.add("heldItem", null);
        }

        return obj;
    }

    public JsonObject getPlayerPosition(ServerPlayer player) {
        JsonObject obj = new JsonObject();
        obj.addProperty("x", player.getX());
        obj.addProperty("y", player.getY());
        obj.addProperty("z", player.getZ());
        obj.addProperty("yaw", player.getYRot());
        obj.addProperty("pitch", player.getXRot());
        obj.addProperty("headYaw", player.getYHeadRot());
        return obj;
    }

    public JsonObject getPlayerInventory(ServerPlayer player) {
        JsonObject obj = new JsonObject();
        Inventory inv = player.getInventory();
        obj.addProperty("selectedSlot", inv.getSelectedSlot());

        JsonArray hotbar = new JsonArray();
        for (int i = 0; i < 9; i++) {
            ItemStack stack = inv.getItem(i);
            if (!stack.isEmpty()) {
                JsonObject slotObj = new JsonObject();
                slotObj.addProperty("slot", i);
                slotObj.addProperty("id", BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
                slotObj.addProperty("count", stack.getCount());
                hotbar.add(slotObj);
            }
        }
        obj.add("hotbar", hotbar);

        JsonArray main = new JsonArray();
        for (int i = 9; i < Inventory.INVENTORY_SIZE; i++) {
            ItemStack stack = inv.getItem(i);
            if (!stack.isEmpty()) {
                JsonObject slotObj = new JsonObject();
                slotObj.addProperty("slot", i);
                slotObj.addProperty("id", BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
                slotObj.addProperty("count", stack.getCount());
                main.add(slotObj);
            }
        }
        obj.add("main", main);

        JsonObject armor = new JsonObject();
        armor.add("head", formatStack(player.getItemBySlot(EquipmentSlot.HEAD)));
        armor.add("chest", formatStack(player.getItemBySlot(EquipmentSlot.CHEST)));
        armor.add("legs", formatStack(player.getItemBySlot(EquipmentSlot.LEGS)));
        armor.add("feet", formatStack(player.getItemBySlot(EquipmentSlot.FEET)));
        obj.add("armor", armor);

        obj.add("offhand", formatStack(player.getItemBySlot(EquipmentSlot.OFFHAND)));

        return obj;
    }

    private JsonObject formatStack(ItemStack stack) {
        if (stack == null || stack.isEmpty()) {
            return null;
        }
        JsonObject obj = new JsonObject();
        obj.addProperty("id", BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
        obj.addProperty("count", stack.getCount());
        return obj;
    }

    public JsonObject getBlockInfo(Level level, BlockPos pos) {
        JsonObject obj = new JsonObject();
        JsonObject posObj = new JsonObject();
        posObj.addProperty("x", pos.getX());
        posObj.addProperty("y", pos.getY());
        posObj.addProperty("z", pos.getZ());
        obj.add("position", posObj);

        if (!level.isLoaded(pos)) {
            if (level instanceof net.minecraft.server.level.ServerLevel sl) {
                sl.getChunk(pos.getX() >> 4, pos.getZ() >> 4, net.minecraft.world.level.chunk.status.ChunkStatus.FULL, true);
            }
        }

        if (!level.isLoaded(pos)) {
            obj.addProperty("loaded", false);
            return obj;
        }
        obj.addProperty("loaded", true);

        BlockState state = level.getBlockState(pos);
        obj.addProperty("blockId", BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString());
        obj.addProperty("blockState", BlockStateParser.serialize(state));

        JsonObject props = new JsonObject();
        state.getValues().forEach(val -> props.addProperty(val.property().getName(), val.valueName()));
        obj.add("properties", props);

        obj.addProperty("isAir", state.isAir());
        obj.addProperty("isSolid", state.isSolid());
        return obj;
    }

    public JsonObject getBlocksInBounds(Level level, BlockPos min, BlockPos max, boolean includeAir) {
        JsonObject res = new JsonObject();
        int dx = Math.abs(max.getX() - min.getX()) + 1;
        int dy = Math.abs(max.getY() - min.getY()) + 1;
        int dz = Math.abs(max.getZ() - min.getZ()) + 1;
        long volume = (long) dx * dy * dz;
        if (volume > 32768) {
            throw new IllegalArgumentException("Scan volume (" + volume + ") exceeds maximum limit (32768)");
        }

        JsonArray blocks = new JsonArray();
        int count = 0;
        for (BlockPos p : BlockPos.betweenClosed(min, max)) {
            if (level.isLoaded(p)) {
                BlockState state = level.getBlockState(p);
                if (!includeAir && state.isAir()) {
                    continue;
                }
                JsonObject blockObj = new JsonObject();
                JsonObject posObj = new JsonObject();
                posObj.addProperty("x", p.getX());
                posObj.addProperty("y", p.getY());
                posObj.addProperty("z", p.getZ());
                blockObj.add("pos", posObj);
                blockObj.addProperty("id", BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString());
                blockObj.addProperty("state", BlockStateParser.serialize(state));
                blocks.add(blockObj);
                count++;
            }
        }
        res.addProperty("count", count);
        res.add("blocks", blocks);
        return res;
    }

    public JsonObject getNearbyEntities(ServerPlayer player, double radius, String filterType) {
        JsonArray entities = new JsonArray();
        Level level = player.level();
        AABB box = AABB.ofSize(player.position(), radius * 2, radius * 2, radius * 2);

        List<Entity> list = level.getEntities(player, box, e -> true);
        for (Entity e : list) {
            boolean include = switch (filterType == null ? "all" : filterType.toLowerCase()) {
                case "living" -> e instanceof LivingEntity;
                case "player" -> e instanceof ServerPlayer;
                case "monster" -> e.getType().getCategory() == MobCategory.MONSTER;
                case "item" -> e instanceof ItemEntity;
                default -> true;
            };
            if (!include) continue;

            JsonObject entityObj = new JsonObject();
            entityObj.addProperty("id", e.getId());
            entityObj.addProperty("uuid", e.getStringUUID());
            entityObj.addProperty("type", BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString());

            JsonObject pos = new JsonObject();
            pos.addProperty("x", e.getX());
            pos.addProperty("y", e.getY());
            pos.addProperty("z", e.getZ());
            entityObj.add("position", pos);

            entityObj.addProperty("distance", player.distanceTo(e));
            entityObj.addProperty("isAlive", e.isAlive());

            if (e instanceof LivingEntity living) {
                entityObj.addProperty("health", living.getHealth());
                entityObj.addProperty("maxHealth", living.getMaxHealth());
            }

            entities.add(entityObj);
        }

        JsonObject output = new JsonObject();
        output.add("entities", entities);
        return output;
    }

    public JsonObject getWorldInfo(Level level) {
        JsonObject obj = new JsonObject();
        obj.addProperty("dimension", level.dimension().identifier().toString());
        long timeOfDay = level.getOverworldClockTime() % 24000L;
        obj.addProperty("timeOfDay", timeOfDay);
        obj.addProperty("gameTime", level.getLevelData().getGameTime());
        obj.addProperty("isDay", timeOfDay < 12000L);
        obj.addProperty("isRaining", level.isRaining());
        obj.addProperty("isThundering", level.isThundering());
        obj.addProperty("minY", level.getMinY());
        obj.addProperty("height", level.getHeight());
        return obj;
    }

    public JsonObject setGameMode(ServerPlayer player, String gameModeStr) {
        GameType target = GameType.byName(gameModeStr != null ? gameModeStr.toLowerCase() : "creative", GameType.CREATIVE);
        String previous = player.gameMode().getName();
        boolean changed = player.setGameMode(target);
        JsonObject res = new JsonObject();
        res.addProperty("player", player.getName().getString());
        res.addProperty("previousGameMode", previous);
        res.addProperty("gameMode", player.gameMode().getName());
        res.addProperty("updated", changed);
        return res;
    }
}
