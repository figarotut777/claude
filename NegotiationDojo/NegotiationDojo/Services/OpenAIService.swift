//
//  OpenAIService.swift
//  NegotiationDojo
//
//  Integrates OpenAI Whisper (STT), GPT-4o (LLM), and TTS
//  Created by Claude on 2025-11-19.
//

import Foundation

@MainActor
class OpenAIService: ObservableObject {
    // MARK: - Configuration
    private let apiKey: String
    private let whisperEndpoint = "https://api.openai.com/v1/audio/transcriptions"
    private let chatEndpoint = "https://api.openai.com/v1/chat/completions"
    private let ttsEndpoint = "https://api.openai.com/v1/audio/speech"

    private let whisperModel = "whisper-1"
    private let chatModel = "gpt-4o"
    private let ttsModel = "tts-1"
    private let ttsVoice = "alloy" // Options: alloy, echo, fable, onyx, nova, shimmer

    // MARK: - Initialization
    init(apiKey: String = "") {
        // In production, load from Keychain or environment
        self.apiKey = apiKey.isEmpty ? ProcessInfo.processInfo.environment["OPENAI_API_KEY"] ?? "" : apiKey
    }

    // MARK: - Speech-to-Text (Whisper)
    func transcribeAudio(fileURL: URL) async throws -> String {
        guard !apiKey.isEmpty else {
            throw OpenAIError.missingAPIKey
        }

        let boundary = UUID().uuidString
        var request = URLRequest(url: URL(string: whisperEndpoint)!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        // Create multipart form data
        var body = Data()

        // Add file
        let audioData = try Data(contentsOf: fileURL)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"audio.m4a\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n".data(using: .utf8)!)

        // Add model
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"model\"\r\n\r\n".data(using: .utf8)!)
        body.append(whisperModel.data(using: .utf8)!)
        body.append("\r\n".data(using: .utf8)!)

        // Add language (optional, but helps with accuracy)
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"language\"\r\n\r\n".data(using: .utf8)!)
        body.append("en".data(using: .utf8)!)
        body.append("\r\n".data(using: .utf8)!)

        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw OpenAIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw OpenAIError.apiError(statusCode: httpResponse.statusCode, message: errorMessage)
        }

        let whisperResponse = try JSONDecoder().decode(WhisperResponse.self, from: data)
        return whisperResponse.text
    }

    // MARK: - Chat Completion (GPT-4o)
    func sendMessage(systemPrompt: String, userMessage: String, currentResistance: Int) async throws -> AIResponse {
        guard !apiKey.isEmpty else {
            throw OpenAIError.missingAPIKey
        }

        // Replace placeholders in system prompt
        let formattedSystemPrompt = systemPrompt
            .replacingOccurrences(of: "{CURRENT_VALUE}", with: "\(currentResistance)")
            .replacingOccurrences(of: "{USER_INPUT}", with: userMessage)

        let messages: [[String: String]] = [
            ["role": "system", "content": formattedSystemPrompt],
            ["role": "user", "content": userMessage]
        ]

        let requestBody: [String: Any] = [
            "model": chatModel,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 500,
            "response_format": ["type": "json_object"]
        ]

        var request = URLRequest(url: URL(string: chatEndpoint)!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw OpenAIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw OpenAIError.apiError(statusCode: httpResponse.statusCode, message: errorMessage)
        }

        let chatResponse = try JSONDecoder().decode(ChatResponse.self, from: data)

        guard let content = chatResponse.choices.first?.message.content else {
            throw OpenAIError.emptyResponse
        }

        // Parse the JSON response from GPT
        guard let jsonData = content.data(using: .utf8) else {
            throw OpenAIError.invalidJSON
        }

        let aiResponse = try JSONDecoder().decode(AIResponse.self, from: jsonData)
        return aiResponse
    }

    // MARK: - Text-to-Speech (TTS)
    func synthesizeSpeech(text: String) async throws -> Data {
        guard !apiKey.isEmpty else {
            throw OpenAIError.missingAPIKey
        }

        let requestBody: [String: Any] = [
            "model": ttsModel,
            "input": text,
            "voice": ttsVoice,
            "response_format": "mp3"
        ]

        var request = URLRequest(url: URL(string: ttsEndpoint)!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw OpenAIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw OpenAIError.apiError(statusCode: httpResponse.statusCode, message: errorMessage)
        }

        return data
    }

    // MARK: - Helper: Save Audio Data to File
    func saveAudioToFile(_ audioData: Data) throws -> URL {
        let tempDir = FileManager.default.temporaryDirectory
        let fileName = "tts_\(Date().timeIntervalSince1970).mp3"
        let fileURL = tempDir.appendingPathComponent(fileName)

        try audioData.write(to: fileURL)
        return fileURL
    }
}

// MARK: - Response Models
private struct WhisperResponse: Codable {
    let text: String
}

private struct ChatResponse: Codable {
    let choices: [Choice]

    struct Choice: Codable {
        let message: Message
    }

    struct Message: Codable {
        let content: String
    }
}

// MARK: - Errors
enum OpenAIError: LocalizedError {
    case missingAPIKey
    case invalidResponse
    case emptyResponse
    case invalidJSON
    case apiError(statusCode: Int, message: String)

    var errorDescription: String? {
        switch self {
        case .missingAPIKey:
            return "OpenAI API key is missing. Please set OPENAI_API_KEY environment variable."
        case .invalidResponse:
            return "Invalid response from OpenAI API."
        case .emptyResponse:
            return "Empty response from OpenAI API."
        case .invalidJSON:
            return "Could not parse JSON response from AI."
        case .apiError(let statusCode, let message):
            return "API Error (\(statusCode)): \(message)"
        }
    }
}
