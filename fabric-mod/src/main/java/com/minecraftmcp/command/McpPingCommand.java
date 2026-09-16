package com.minecraftmcp.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

/**
 * Minimal verification command: /mcp ping
 * Responds with a confirmation message to verify the Fabric server-side mod is loaded.
 */
public class McpPingCommand {
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
            Commands.literal("mcp")
                .then(
                    Commands.literal("ping")
                        .executes(McpPingCommand::executePing)
                )
        );
    }

    private static int executePing(CommandContext<CommandSourceStack> context) {
        CommandSourceStack source = context.getSource();
        source.sendSuccess(() -> Component.literal("Pong from Minecraft MCP Bridge (Minecraft 26.2)!"), false);
        return 1;
    }
}

