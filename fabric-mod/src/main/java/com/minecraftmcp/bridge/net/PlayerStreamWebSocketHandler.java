package com.minecraftmcp.bridge.net;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.minecraftmcp.bridge.service.ObservationService;
import io.netty.channel.Channel;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.group.ChannelGroup;
import io.netty.channel.group.DefaultChannelGroup;
import io.netty.handler.codec.http.websocketx.TextWebSocketFrame;
import io.netty.util.concurrent.GlobalEventExecutor;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@ChannelHandler.Sharable
public class PlayerStreamWebSocketHandler extends SimpleChannelInboundHandler<TextWebSocketFrame> {
    private static final Logger LOGGER = LoggerFactory.getLogger("minecraft-mcp-bridge");
    private static PlayerStreamWebSocketHandler INSTANCE;

    private final ChannelGroup channels = new DefaultChannelGroup(GlobalEventExecutor.INSTANCE);
    private final Map<Channel, String> channelPlayerSubscriptions = new ConcurrentHashMap<>();

    public static synchronized PlayerStreamWebSocketHandler getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new PlayerStreamWebSocketHandler();
        }
        return INSTANCE;
    }

    private PlayerStreamWebSocketHandler() {}

    @Override
    public void handlerAdded(ChannelHandlerContext ctx) {
        channels.add(ctx.channel());
    }

    @Override
    public void handlerRemoved(ChannelHandlerContext ctx) {
        channels.remove(ctx.channel());
        channelPlayerSubscriptions.remove(ctx.channel());
    }

    @Override
    protected void channelRead0(ChannelHandlerContext ctx, TextWebSocketFrame msg) {
        try {
            JsonObject json = JsonParser.parseString(msg.text()).getAsJsonObject();
            String action = json.has("action") ? json.get("action").getAsString() : "";
            if ("subscribe".equalsIgnoreCase(action)) {
                String targetPlayer = json.has("player") ? json.get("player").getAsString() : "";
                channelPlayerSubscriptions.put(ctx.channel(), targetPlayer);
                JsonObject ack = new JsonObject();
                ack.addProperty("event", "subscribed");
                ack.addProperty("player", targetPlayer);
                ctx.channel().writeAndFlush(new TextWebSocketFrame(ack.toString()));
            } else if ("unsubscribe".equalsIgnoreCase(action)) {
                channelPlayerSubscriptions.remove(ctx.channel());
                JsonObject ack = new JsonObject();
                ack.addProperty("event", "unsubscribed");
                ctx.channel().writeAndFlush(new TextWebSocketFrame(ack.toString()));
            }
        } catch (Exception e) {
            LOGGER.warn("[Minecraft MCP] Failed to parse WebSocket incoming frame: {}", e.getMessage());
        }
    }

    public void broadcastTick(MinecraftServer server, long tick) {
        if (channels.isEmpty() || server == null) {
            return;
        }

        ObservationService obs = ObservationService.getInstance();
        for (Channel ch : channels) {
            if (!ch.isActive()) continue;

            String playerTarget = channelPlayerSubscriptions.getOrDefault(ch, "");
            ServerPlayer player = obs.resolvePlayer(server, playerTarget);
            if (player == null) continue;

            JsonObject event = new JsonObject();
            event.addProperty("event", "player_tick");
            event.addProperty("tick", tick);
            event.addProperty("player", player.getName().getString());

            JsonObject pos = new JsonObject();
            pos.addProperty("x", player.getX());
            pos.addProperty("y", player.getY());
            pos.addProperty("z", player.getZ());
            event.add("pos", pos);

            JsonObject rot = new JsonObject();
            rot.addProperty("yaw", player.getYRot());
            rot.addProperty("pitch", player.getXRot());
            rot.addProperty("headYaw", player.getYHeadRot());
            event.add("rot", rot);

            event.addProperty("health", player.getHealth());
            event.addProperty("food", player.getFoodData().getFoodLevel());

            ch.writeAndFlush(new TextWebSocketFrame(event.toString()));
        }
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        LOGGER.warn("[Minecraft MCP] WebSocket channel exception: {}", cause.getMessage());
        ctx.close();
    }
}

