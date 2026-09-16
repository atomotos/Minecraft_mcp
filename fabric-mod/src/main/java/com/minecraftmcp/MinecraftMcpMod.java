package com.minecraftmcp;

import com.minecraftmcp.bridge.net.HttpBridgeServer;
import com.minecraftmcp.bridge.net.PlayerStreamWebSocketHandler;
import com.minecraftmcp.bridge.scheduler.TickSchedulerService;
import com.minecraftmcp.command.McpPingCommand;
import net.fabricmc.api.DedicatedServerModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Server-side entrypoint for Minecraft MCP Bridge.
 * Initializes the mod and registers the minimal /mcp ping verification command.
 * Initializes the mod, registers commands, and starts the embedded HTTP/WebSocket bridge server.
 */
public class MinecraftMcpMod implements DedicatedServerModInitializer {
    public static final String MOD_ID = "minecraft-mcp-bridge";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
    public static final int BRIDGE_PORT = 25585;

    @Override
    public void onInitializeServer() {
        LOGGER.info("[Minecraft MCP] Initializing minimal server-side mod for Minecraft 26.2...");
        LOGGER.info("[Minecraft MCP] Initializing Minecraft MCP Bridge mod for Minecraft 26.2...");

        // Register /mcp ping command via Fabric CommandRegistrationCallback
        // 1. Initialize TickSchedulerService
        TickSchedulerService scheduler = TickSchedulerService.getInstance();

        // 2. Register command
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
            McpPingCommand.register(dispatcher);
        });

        LOGGER.info("[Minecraft MCP] Registered /mcp ping command successfully.");
        // 3. Register ServerLifecycleEvents for Netty Bridge Server
        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            scheduler.setServer(server);
            HttpBridgeServer.getInstance().start(BRIDGE_PORT);
        });

        ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
            HttpBridgeServer.getInstance().stop();
        });

        // 4. Register WebSocket player stream broadcast on end server tick
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            PlayerStreamWebSocketHandler.getInstance().broadcastTick(server, scheduler.getCurrentTick());
        });

        LOGGER.info("[Minecraft MCP] Mod initialized. Bridge configured for port {}.", BRIDGE_PORT);
    }
}

