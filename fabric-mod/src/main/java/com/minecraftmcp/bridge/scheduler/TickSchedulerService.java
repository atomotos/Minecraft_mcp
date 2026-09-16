package com.minecraftmcp.bridge.scheduler;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.server.MinecraftServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

/**
 * Service ensuring thread-safe execution of tasks on the Minecraft server tick thread.
 * Submits tasks directly to MinecraftServer.execute() for immediate event-loop scheduling,
 * while maintaining tick counting on ServerTickEvents.END_SERVER_TICK.
 */
public class TickSchedulerService {
    private static final Logger LOGGER = LoggerFactory.getLogger("minecraft-mcp-bridge");
    private static TickSchedulerService INSTANCE;

    private final ConcurrentLinkedQueue<Runnable> pendingPreStartQueue = new ConcurrentLinkedQueue<>();
    private final AtomicLong currentTick = new AtomicLong(0);
    private volatile MinecraftServer server;

    public static synchronized TickSchedulerService getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new TickSchedulerService();
        }
        return INSTANCE;
    }

    private TickSchedulerService() {
        ServerTickEvents.END_SERVER_TICK.register(this::onServerTick);
    }

    public void setServer(MinecraftServer server) {
        this.server = server;
        // Drain any tasks that arrived before server started
        Runnable task;
        while ((task = pendingPreStartQueue.poll()) != null) {
            server.execute(task);
        }
    }

    public MinecraftServer getServer() {
        return this.server;
    }

    public long getCurrentTick() {
        return currentTick.get();
    }

    private void onServerTick(MinecraftServer server) {
        this.server = server;
        currentTick.incrementAndGet();
    }

    /**
     * Enqueue a supplier returning a result on the server thread.
     */
    public <T> CompletableFuture<T> enqueue(Supplier<T> supplier) {
        CompletableFuture<T> future = new CompletableFuture<>();
        Runnable task = () -> {
            try {
                future.complete(supplier.get());
            } catch (Throwable t) {
                LOGGER.error("[Minecraft MCP] Error executing server tick task", t);
                future.completeExceptionally(t);
            }
        };

        if (server != null) {
            server.execute(task);
        } else {
            pendingPreStartQueue.add(task);
        }
        return future;
    }

    /**
     * Enqueue a runnable task on the server thread.
     */
    public CompletableFuture<Void> enqueue(Runnable runnable) {
        CompletableFuture<Void> future = new CompletableFuture<>();
        Runnable task = () -> {
            try {
                runnable.run();
                future.complete(null);
            } catch (Throwable t) {
                LOGGER.error("[Minecraft MCP] Error executing server tick task", t);
                future.completeExceptionally(t);
            }
        };

        if (server != null) {
            server.execute(task);
        } else {
            pendingPreStartQueue.add(task);
        }
        return future;
    }
}

