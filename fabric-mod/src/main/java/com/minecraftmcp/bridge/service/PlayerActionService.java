package com.minecraftmcp.bridge.service;

import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.concurrent.atomic.AtomicBoolean;

public class PlayerActionService {
    private static PlayerActionService INSTANCE;
    private final AtomicBoolean movementCancelled = new AtomicBoolean(false);

    public static synchronized PlayerActionService getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new PlayerActionService();
        }
        return INSTANCE;
    }

    private PlayerActionService() {}

    public JsonObject teleport(ServerPlayer player, double x, double y, double z, Float yaw, Float pitch) {
        float useYaw = (yaw != null) ? yaw : player.getYRot();
        float usePitch = (pitch != null) ? pitch : player.getXRot();

        player.teleportTo(x, y, z);
        player.setYRot(useYaw);
        player.setXRot(usePitch);
        player.setYHeadRot(useYaw);

        JsonObject data = new JsonObject();
        data.addProperty("action", "teleport");
        data.addProperty("teleported", true);

        JsonObject posObj = new JsonObject();
        posObj.addProperty("x", player.getX());
        posObj.addProperty("y", player.getY());
        posObj.addProperty("z", player.getZ());
        posObj.addProperty("yaw", player.getYRot());
        posObj.addProperty("pitch", player.getXRot());
        data.add("position", posObj);

        return data;
    }

    public JsonObject setRotation(ServerPlayer player, float yaw, float pitch) {
        player.setYRot(yaw);
        player.setXRot(pitch);
        player.setYHeadRot(yaw);

        JsonObject data = new JsonObject();
        data.addProperty("action", "rotate");
        data.addProperty("yaw", yaw);
        data.addProperty("pitch", pitch);
        return data;
    }

    public JsonObject selectSlot(ServerPlayer player, int slotIndex) {
        if (slotIndex < 0 || slotIndex > 8) {
            throw new IllegalArgumentException("Slot index must be between 0 and 8, got " + slotIndex);
        }
        player.getInventory().setSelectedSlot(slotIndex);

        JsonObject data = new JsonObject();
        data.addProperty("action", "select_slot");
        data.addProperty("selectedSlot", slotIndex);
        return data;
    }

    public JsonObject useItem(ServerPlayer player, InteractionHand hand) {
        InteractionHand useHand = (hand != null) ? hand : InteractionHand.MAIN_HAND;
        ItemStack heldItem = player.getItemInHand(useHand);
        InteractionResult res = player.gameMode.useItem(player, player.level(), heldItem, useHand);

        JsonObject data = new JsonObject();
        data.addProperty("action", "use_item");
        data.addProperty("hand", useHand.name());
        data.addProperty("result", res.toString());
        data.addProperty("success", res.consumesAction());
        return data;
    }

    public JsonObject dropItem(ServerPlayer player, boolean dropEntireStack) {
        player.drop(dropEntireStack);

        JsonObject data = new JsonObject();
        data.addProperty("action", "drop");
        data.addProperty("dropped", true);
        data.addProperty("entire_stack", dropEntireStack);
        return data;
    }

    public JsonObject swingHand(ServerPlayer player, InteractionHand hand) {
        InteractionHand useHand = (hand != null) ? hand : InteractionHand.MAIN_HAND;
        player.swing(useHand);

        JsonObject data = new JsonObject();
        data.addProperty("action", "swing");
        data.addProperty("hand", useHand.name());
        data.addProperty("swung", true);
        return data;
    }

    public JsonObject moveTowards(ServerPlayer player, double targetX, double targetY, double targetZ, double speedMultiplier, double tolerance) {
        movementCancelled.set(false);
        Vec3 startPos = player.position();
        double startX = startPos.x;
        double startY = startPos.y;
        double startZ = startPos.z;

        double dx = targetX - startX;
        double dy = targetY - startY;
        double dz = targetZ - startZ;
        double distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

        double tol = (tolerance > 0.0) ? tolerance : 1.0;
        if (distance <= tol) {
            JsonObject data = new JsonObject();
            data.addProperty("action", "move_to");
            data.add("start_position", formatVec3(startPos));
            data.add("current_position", formatVec3(player.position()));
            data.add("target_position", formatPos(targetX, targetY, targetZ));
            data.addProperty("status", "reached");
            data.addProperty("distance_remaining", 0.0);
            return data;
        }

        Level level = player.level();
        BlockPos targetBlockPos = new BlockPos((int) Math.floor(targetX), (int) Math.floor(targetY), (int) Math.floor(targetZ));
        BlockState targetBlockState = level.getBlockState(targetBlockPos);
        BlockState targetHeadState = level.getBlockState(targetBlockPos.above());

        // Stuck detection: if target block is solid or obstructed and cannot be stepped into
        if (targetBlockState.isSolid() && targetHeadState.isSolid()) {
            JsonObject data = new JsonObject();
            data.addProperty("action", "move_to");
            data.add("start_position", formatVec3(startPos));
            data.add("current_position", formatVec3(player.position()));
            data.add("target_position", formatPos(targetX, targetY, targetZ));
            data.addProperty("status", "stuck");
            data.addProperty("distance_remaining", Math.round(distance * 100.0) / 100.0);
            return data;
        }

        // Check if movement was cancelled
        if (movementCancelled.get()) {
            JsonObject data = new JsonObject();
            data.addProperty("action", "move_to");
            data.add("start_position", formatVec3(startPos));
            data.add("current_position", formatVec3(player.position()));
            data.add("target_position", formatPos(targetX, targetY, targetZ));
            data.addProperty("status", "cancelled");
            data.addProperty("distance_remaining", Math.round(distance * 100.0) / 100.0);
            return data;
        }

        // Basic waypoint locomotion: step towards destination
        // If distance is reasonable (<= 10 blocks) and unblocked, advance to target position directly
        // Otherwise step by incremental fraction
        double stepSize = Math.max(1.0, speedMultiplier * 2.0);
        double ratio = Math.min(1.0, stepSize / distance);

        double nextX = startX + dx * ratio;
        double nextY = startY + dy * ratio;
        double nextZ = startZ + dz * ratio;

        BlockPos nextFoot = new BlockPos((int) Math.floor(nextX), (int) Math.floor(nextY), (int) Math.floor(nextZ));
        BlockPos nextHead = nextFoot.above();
        if (level.getBlockState(nextFoot).isSolid() && level.getBlockState(nextHead).isSolid()) {
            // Path is blocked ahead
            JsonObject data = new JsonObject();
            data.addProperty("action", "move_to");
            data.add("start_position", formatVec3(startPos));
            data.add("current_position", formatVec3(player.position()));
            data.add("target_position", formatPos(targetX, targetY, targetZ));
            data.addProperty("status", "stuck");
            data.addProperty("distance_remaining", Math.round(distance * 100.0) / 100.0);
            return data;
        }

        // Advance player position
        player.teleportTo(nextX, nextY, nextZ);

        double remainingDist = Math.sqrt(
                Math.pow(targetX - player.getX(), 2) +
                Math.pow(targetY - player.getY(), 2) +
                Math.pow(targetZ - player.getZ(), 2)
        );

        String status = (remainingDist <= tol) ? "reached" : "moving";

        JsonObject data = new JsonObject();
        data.addProperty("action", "move_to");
        data.add("start_position", formatVec3(startPos));
        data.add("current_position", formatVec3(player.position()));
        data.add("target_position", formatPos(targetX, targetY, targetZ));
        data.addProperty("status", status);
        data.addProperty("distance_remaining", Math.round(remainingDist * 100.0) / 100.0);
        return data;
    }

    public JsonObject stopMovement(ServerPlayer player) {
        movementCancelled.set(true);

        JsonObject data = new JsonObject();
        data.addProperty("action", "stop_movement");
        data.add("final_position", formatVec3(player.position()));
        data.addProperty("status", "cancelled");
        return data;
    }

    private JsonObject formatVec3(Vec3 vec) {
        JsonObject obj = new JsonObject();
        obj.addProperty("x", Math.round(vec.x * 100.0) / 100.0);
        obj.addProperty("y", Math.round(vec.y * 100.0) / 100.0);
        obj.addProperty("z", Math.round(vec.z * 100.0) / 100.0);
        return obj;
    }

    private JsonObject formatPos(double x, double y, double z) {
        JsonObject obj = new JsonObject();
        obj.addProperty("x", Math.round(x * 100.0) / 100.0);
        obj.addProperty("y", Math.round(y * 100.0) / 100.0);
        obj.addProperty("z", Math.round(z * 100.0) / 100.0);
        return obj;
    }
}
