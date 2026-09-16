package com.minecraftmcp.bridge.dto;

import com.google.gson.JsonObject;

public class ApiResponse {
    public static JsonObject success(com.google.gson.JsonElement data, long tick) {
        JsonObject res = new JsonObject();
        res.addProperty("success", true);
        res.add("data", data);
        res.add("error", null);
        res.addProperty("tick", tick);
        return res;
    }

    public static JsonObject error(String code, String message, long tick) {
        JsonObject res = new JsonObject();
        res.addProperty("success", false);
        res.add("data", null);
        JsonObject err = new JsonObject();
        err.addProperty("code", code);
        err.addProperty("message", message);
        res.add("error", err);
        res.addProperty("tick", tick);
        return res;
    }
}

