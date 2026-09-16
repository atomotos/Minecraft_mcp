package com.minecraftmcp.bridge.net;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.minecraftmcp.bridge.dto.ApiResponse;
import com.minecraftmcp.bridge.scheduler.TickSchedulerService;
import com.minecraftmcp.bridge.service.ObservationService;
import com.minecraftmcp.bridge.service.PlayerActionService;
import com.minecraftmcp.bridge.service.WorldMutationService;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.codec.http.*;
import io.netty.util.CharsetUtil;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

@ChannelHandler.Sharable
public class RestDispatcherHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
    private static final Logger LOGGER = LoggerFactory.getLogger("minecraft-mcp-bridge");
    private static RestDispatcherHandler INSTANCE;

    public static synchronized RestDispatcherHandler getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new RestDispatcherHandler();
        }
        return INSTANCE;
    }

    private RestDispatcherHandler() {}

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest request) {
        if (!request.decoderResult().isSuccess()) {
            sendError(ctx, HttpResponseStatus.BAD_REQUEST, "INVALID_REQUEST", "Malformed HTTP request", request);
            return;
        }

        QueryStringDecoder decoder = new QueryStringDecoder(request.uri());
        String path = decoder.path();
        HttpMethod method = request.method();
        Map<String, List<String>> params = decoder.parameters();

        TickSchedulerService scheduler = TickSchedulerService.getInstance();
        MinecraftServer server = scheduler.getServer();
        if (server == null) {
            sendError(ctx, HttpResponseStatus.SERVICE_UNAVAILABLE, "NOT_READY", "Minecraft server is not ready", request);
            return;
        }

        ObservationService obs = ObservationService.getInstance();
        long tick = scheduler.getCurrentTick();

        try {
            if (HttpMethod.GET.equals(method) && ("/api/v1/status".equals(path) || "/api/status".equals(path))) {
                handleStatus(ctx, server, tick, request);
            } else if (HttpMethod.GET.equals(method) && "/api/v1/player/status".equals(path)) {
                String target = getQueryParam(params, "player");
                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, target);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found: " + target, scheduler.getCurrentTick());
                    }
                    return ApiResponse.success(obs.getPlayerStatus(player), scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.GET.equals(method) && "/api/v1/player/position".equals(path)) {
                String target = getQueryParam(params, "player");
                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, target);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found: " + target, scheduler.getCurrentTick());
                    }
                    return ApiResponse.success(obs.getPlayerPosition(player), scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.GET.equals(method) && "/api/v1/player/inventory".equals(path)) {
                String target = getQueryParam(params, "player");
                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, target);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found: " + target, scheduler.getCurrentTick());
                    }
                    return ApiResponse.success(obs.getPlayerInventory(player), scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/gamemode".equals(path)) {
                JsonObject body = parseJsonBody(request);
                String p = getJsonString(body, "player");
                final String targetPlayer = (p != null) ? p : getQueryParam(params, "player");
                String m = getJsonString(body, "gameMode");
                final String mode = (m != null) ? m : getQueryParam(params, "gameMode", "creative");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found: " + targetPlayer, scheduler.getCurrentTick());
                    }
                    JsonObject res = obs.setGameMode(player, mode);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.GET.equals(method) && "/api/v1/world/block".equals(path)) {
                int x = Integer.parseInt(getQueryParam(params, "x", "0"));
                int y = Integer.parseInt(getQueryParam(params, "y", "64"));
                int z = Integer.parseInt(getQueryParam(params, "z", "0"));
                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    JsonObject blockData = obs.getBlockInfo(level, new BlockPos(x, y, z));
                    return ApiResponse.success(blockData, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/world/blocks".equals(path)) {
                String bodyStr = request.content().toString(CharsetUtil.UTF_8);
                JsonObject body = JsonParser.parseString(bodyStr).getAsJsonObject();
                JsonObject minObj = body.getAsJsonObject("min");
                JsonObject maxObj = body.getAsJsonObject("max");
                boolean includeAir = body.has("includeAir") && body.get("includeAir").getAsBoolean();

                BlockPos min = new BlockPos(minObj.get("x").getAsInt(), minObj.get("y").getAsInt(), minObj.get("z").getAsInt());
                BlockPos max = new BlockPos(maxObj.get("x").getAsInt(), maxObj.get("y").getAsInt(), maxObj.get("z").getAsInt());

                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    JsonObject blocksData = obs.getBlocksInBounds(level, min, max, includeAir);
                    return ApiResponse.success(blocksData, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "SCAN_FAILED", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.GET.equals(method) && "/api/v1/world/entities".equals(path)) {
                double radius = Double.parseDouble(getQueryParam(params, "radius", "16.0"));
                String type = getQueryParam(params, "type", "all");
                String playerTarget = getQueryParam(params, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, playerTarget);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not found to anchor search radius", scheduler.getCurrentTick());
                    }
                    JsonObject entities = obs.getNearbyEntities(player, radius, type);
                    return ApiResponse.success(entities, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.GET.equals(method) && "/api/v1/world/info".equals(path)) {
                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    JsonObject info = obs.getWorldInfo(level);
                    return ApiResponse.success(info, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/world/set_block".equals(path)) {
                JsonObject body = parseJsonBody(request);
                int x = body.get("x").getAsInt();
                int y = body.get("y").getAsInt();
                int z = body.get("z").getAsInt();
                String blockState = body.get("blockState").getAsString();
                int flags = body.has("flags") ? body.get("flags").getAsInt() : 11;

                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    JsonObject res = WorldMutationService.getInstance().setBlock(level, new BlockPos(x, y, z), blockState, flags);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "SET_BLOCK_FAILED", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.POST.equals(method) && "/api/v1/world/break_block".equals(path)) {
                JsonObject body = parseJsonBody(request);
                int x = body.get("x").getAsInt();
                int y = body.get("y").getAsInt();
                int z = body.get("z").getAsInt();
                boolean dropResources = !body.has("dropResources") || body.get("dropResources").getAsBoolean();
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    JsonObject res = WorldMutationService.getInstance().breakBlock(level, new BlockPos(x, y, z), dropResources, player);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "BREAK_BLOCK_FAILED", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.POST.equals(method) && "/api/v1/world/fill".equals(path)) {
                JsonObject body = parseJsonBody(request);
                JsonObject fromObj = body.getAsJsonObject("from");
                JsonObject toObj = body.getAsJsonObject("to");
                BlockPos from = new BlockPos(fromObj.get("x").getAsInt(), fromObj.get("y").getAsInt(), fromObj.get("z").getAsInt());
                BlockPos to = new BlockPos(toObj.get("x").getAsInt(), toObj.get("y").getAsInt(), toObj.get("z").getAsInt());
                String blockState = body.get("blockState").getAsString();
                String replaceFilter = getJsonString(body, "replaceFilter");

                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    JsonObject res = WorldMutationService.getInstance().fillRegion(level, from, to, blockState, replaceFilter);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "FILL_REGION_FAILED", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.POST.equals(method) && "/api/v1/world/interact".equals(path)) {
                JsonObject body = parseJsonBody(request);
                int x = body.get("x").getAsInt();
                int y = body.get("y").getAsInt();
                int z = body.get("z").getAsInt();
                String handStr = getJsonString(body, "hand");
                if (handStr == null) handStr = "main_hand";
                net.minecraft.world.InteractionHand hand = "off_hand".equalsIgnoreCase(handStr) ? net.minecraft.world.InteractionHand.OFF_HAND : net.minecraft.world.InteractionHand.MAIN_HAND;
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerLevel level = server.overworld();
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = WorldMutationService.getInstance().interactWithBlock(level, player, new BlockPos(x, y, z), hand);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "INTERACT_FAILED", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/move".equals(path)) {
                JsonObject body = parseJsonBody(request);
                double x = body.get("x").getAsDouble();
                double y = body.get("y").getAsDouble();
                double z = body.get("z").getAsDouble();
                double speed = body.has("speed") ? body.get("speed").getAsDouble() : 1.0;
                double tolerance = body.has("tolerance") ? body.get("tolerance").getAsDouble() : 1.0;
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().moveTowards(player, x, y, z, speed, tolerance);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/stop".equals(path)) {
                JsonObject body = parseJsonBody(request);
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().stopMovement(player);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/teleport".equals(path)) {
                JsonObject body = parseJsonBody(request);
                double x = body.get("x").getAsDouble();
                double y = body.get("y").getAsDouble();
                double z = body.get("z").getAsDouble();
                Float yaw = body.has("yaw") ? body.get("yaw").getAsFloat() : null;
                Float pitch = body.has("pitch") ? body.get("pitch").getAsFloat() : null;
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().teleport(player, x, y, z, yaw, pitch);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/rotate".equals(path)) {
                JsonObject body = parseJsonBody(request);
                float yaw = body.get("yaw").getAsFloat();
                float pitch = body.get("pitch").getAsFloat();
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().setRotation(player, yaw, pitch);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/select_slot".equals(path)) {
                JsonObject body = parseJsonBody(request);
                int slot = body.get("slot").getAsInt();
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().selectSlot(player, slot);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request))
                  .exceptionally(ex -> {
                      sendError(ctx, HttpResponseStatus.BAD_REQUEST, "INVALID_SLOT", ex.getMessage(), request);
                      return null;
                  });
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/use_item".equals(path)) {
                JsonObject body = parseJsonBody(request);
                String handStr = getJsonString(body, "hand");
                if (handStr == null) handStr = "main_hand";
                net.minecraft.world.InteractionHand hand = "off_hand".equalsIgnoreCase(handStr) ? net.minecraft.world.InteractionHand.OFF_HAND : net.minecraft.world.InteractionHand.MAIN_HAND;
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().useItem(player, hand);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/drop".equals(path)) {
                JsonObject body = parseJsonBody(request);
                boolean entireStack = body != null && body.has("entireStack") && body.get("entireStack").getAsBoolean();
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().dropItem(player, entireStack);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else if (HttpMethod.POST.equals(method) && "/api/v1/player/swing".equals(path)) {
                JsonObject body = parseJsonBody(request);
                String handStr = getJsonString(body, "hand");
                if (handStr == null) handStr = "main_hand";
                net.minecraft.world.InteractionHand hand = "off_hand".equalsIgnoreCase(handStr) ? net.minecraft.world.InteractionHand.OFF_HAND : net.minecraft.world.InteractionHand.MAIN_HAND;
                String targetPlayer = getJsonString(body, "player");

                scheduler.enqueue(() -> {
                    ServerPlayer player = obs.resolvePlayer(server, targetPlayer);
                    if (player == null) {
                        return ApiResponse.error("PLAYER_NOT_FOUND", "Player not online or found", scheduler.getCurrentTick());
                    }
                    JsonObject res = PlayerActionService.getInstance().swingHand(player, hand);
                    return ApiResponse.success(res, scheduler.getCurrentTick());
                }).thenAccept(json -> sendJsonResponse(ctx, HttpResponseStatus.OK, json, request));
            } else {
                sendError(ctx, HttpResponseStatus.NOT_FOUND, "ENDPOINT_NOT_FOUND", "No endpoint matches: " + path, request);
            }
        } catch (Exception ex) {
            LOGGER.error("[Minecraft MCP] Request dispatch failed", ex);
            sendError(ctx, HttpResponseStatus.INTERNAL_SERVER_ERROR, "SERVER_ERROR", ex.getMessage(), request);
        }
    }

    private void handleStatus(ChannelHandlerContext ctx, MinecraftServer server, long tick, FullHttpRequest request) {
        long avgNanos = server.getAverageTickTimeNanos();
        double mspt = avgNanos / 1_000_000.0;
        double tps = Math.min(20.0, 1000.0 / Math.max(mspt, 1.0));

        JsonObject data = new JsonObject();
        data.addProperty("connected", true);
        data.addProperty("minecraft_version", server.getServerVersion());
        data.addProperty("tps", Math.round(tps * 100.0) / 100.0);
        data.addProperty("mspt", Math.round(mspt * 100.0) / 100.0);
        data.addProperty("player_count", server.getPlayerList().getPlayerCount());
        data.addProperty("max_players", server.getPlayerList().getMaxPlayers());

        JsonArray players = new JsonArray();
        for (ServerPlayer sp : server.getPlayerList().getPlayers()) {
            players.add(sp.getName().getString());
        }
        data.add("players", players);

        JsonObject response = ApiResponse.success(data, tick);
        sendJsonResponse(ctx, HttpResponseStatus.OK, response, request);
    }

    private String getQueryParam(Map<String, List<String>> params, String key) {
        List<String> list = params.get(key);
        return (list != null && !list.isEmpty()) ? list.get(0) : null;
    }

    private String getQueryParam(Map<String, List<String>> params, String key, String defaultVal) {
        String val = getQueryParam(params, key);
        return val != null ? val : defaultVal;
    }

    private void sendJsonResponse(ChannelHandlerContext ctx, HttpResponseStatus status, JsonObject json, FullHttpRequest request) {
        byte[] bytes = json.toString().getBytes(CharsetUtil.UTF_8);
        FullHttpResponse response = new DefaultFullHttpResponse(
                HttpVersion.HTTP_1_1,
                status,
                Unpooled.wrappedBuffer(bytes)
        );
        response.headers().set(HttpHeaderNames.CONTENT_TYPE, "application/json; charset=UTF-8");
        response.headers().set(HttpHeaderNames.CONTENT_LENGTH, bytes.length);

        boolean keepAlive = HttpUtil.isKeepAlive(request);
        if (keepAlive) {
            response.headers().set(HttpHeaderNames.CONNECTION, HttpHeaderValues.KEEP_ALIVE);
            ctx.writeAndFlush(response);
        } else {
            ctx.writeAndFlush(response).addListener(ChannelFutureListener.CLOSE);
        }
    }

    private JsonObject parseJsonBody(FullHttpRequest request) {
        String bodyStr = request.content().toString(CharsetUtil.UTF_8);
        if (bodyStr == null || bodyStr.isBlank()) {
            return new JsonObject();
        }
        try {
            JsonElement el = JsonParser.parseString(bodyStr);
            return el.isJsonObject() ? el.getAsJsonObject() : new JsonObject();
        } catch (Exception e) {
            return new JsonObject();
        }
    }

    private String getJsonString(JsonObject obj, String memberName) {
        if (obj != null && obj.has(memberName) && !obj.get(memberName).isJsonNull()) {
            return obj.get(memberName).getAsString();
        }
        return null;
    }

    private void sendError(ChannelHandlerContext ctx, HttpResponseStatus status, String code, String message, FullHttpRequest request) {
        long tick = TickSchedulerService.getInstance().getCurrentTick();
        JsonObject err = ApiResponse.error(code, message, tick);
        sendJsonResponse(ctx, status, err, request);
    }
}

