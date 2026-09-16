package com.minecraftmcp.bridge.net;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelPipeline;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.http.HttpObjectAggregator;
import io.netty.handler.codec.http.HttpServerCodec;
import io.netty.handler.codec.http.websocketx.WebSocketServerProtocolHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HttpBridgeServer {
    private static final Logger LOGGER = LoggerFactory.getLogger("minecraft-mcp-bridge");
    private static HttpBridgeServer INSTANCE;

    private EventLoopGroup bossGroup;
    private EventLoopGroup workerGroup;
    private Channel serverChannel;
    private boolean running = false;

    public static synchronized HttpBridgeServer getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new HttpBridgeServer();
        }
        return INSTANCE;
    }

    private HttpBridgeServer() {}

    public synchronized void start(int port) {
        if (running) {
            return;
        }
        LOGGER.info("[Minecraft MCP] Starting embedded Netty Bridge Server on 127.0.0.1:{}...", port);

        bossGroup = new NioEventLoopGroup(1);
        workerGroup = new NioEventLoopGroup(2);

        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ChannelPipeline p = ch.pipeline();
                     p.addLast(new HttpServerCodec());
                     p.addLast(new HttpObjectAggregator(65536));
                     p.addLast(new WebSocketServerProtocolHandler("/api/v1/ws/player"));
                     p.addLast(PlayerStreamWebSocketHandler.getInstance());
                     p.addLast(RestDispatcherHandler.getInstance());
                 }
             });

            serverChannel = b.bind("127.0.0.1", port).sync().channel();
            running = true;
            LOGGER.info("[Minecraft MCP] Netty Bridge Server successfully listening on http://127.0.0.1:{}", port);
        } catch (Exception e) {
            LOGGER.error("[Minecraft MCP] Failed to bind Netty Bridge Server on port " + port, e);
            stop();
        }
    }

    public synchronized void stop() {
        if (!running && bossGroup == null && workerGroup == null) {
            return;
        }
        LOGGER.info("[Minecraft MCP] Shutting down Netty Bridge Server...");
        try {
            if (serverChannel != null) {
                serverChannel.close().syncUninterruptibly();
            }
        } catch (Exception ignored) {}

        if (bossGroup != null) {
            bossGroup.shutdownGracefully();
        }
        if (workerGroup != null) {
            workerGroup.shutdownGracefully();
        }

        running = false;
        LOGGER.info("[Minecraft MCP] Netty Bridge Server stopped.");
    }

    public boolean isRunning() {
        return running;
    }
}

