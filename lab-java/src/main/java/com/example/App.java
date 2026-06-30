package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("lab-java running");
    }

    // 簡單的字串拼接 SQL（供 semgrep 找到）
    public String getUser(String userId) {
        String query = "SELECT * FROM users WHERE id = '" + userId + "'";
        return query;
    }
}
