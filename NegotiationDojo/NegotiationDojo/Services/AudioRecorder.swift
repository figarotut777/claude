//
//  AudioRecorder.swift
//  NegotiationDojo
//
//  Phase 1: Audio Foundation
//  Created by Claude on 2025-11-19.
//

import Foundation
import AVFoundation
import Combine

@MainActor
class AudioRecorder: NSObject, ObservableObject {
    // MARK: - Published Properties
    @Published var isRecording = false
    @Published var isPlaying = false
    @Published var recordingLevel: Float = 0.0
    @Published var errorMessage: String?

    // MARK: - Private Properties
    private var audioRecorder: AVAudioRecorder?
    private var audioPlayer: AVAudioPlayer?
    private var recordingURL: URL?
    private var levelTimer: Timer?

    // MARK: - Audio Session Setup
    func setupAudioSession() async throws {
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.playAndRecord, mode: .default)
        try audioSession.setActive(true)

        // Request microphone permission
        let permissionGranted = await audioSession.requestRecordPermission()
        if !permissionGranted {
            throw AudioRecorderError.permissionDenied
        }
    }

    // MARK: - Recording
    func startRecording() async throws {
        // Stop any existing recording
        stopRecording()

        // Setup audio session
        try await setupAudioSession()

        // Create temporary file URL
        let tempDir = FileManager.default.temporaryDirectory
        let fileName = "recording_\(Date().timeIntervalSince1970).m4a"
        recordingURL = tempDir.appendingPathComponent(fileName)

        guard let url = recordingURL else {
            throw AudioRecorderError.invalidURL
        }

        // Configure recording settings
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100.0,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]

        // Create and start recorder
        audioRecorder = try AVAudioRecorder(url: url, settings: settings)
        audioRecorder?.delegate = self
        audioRecorder?.isMeteringEnabled = true

        guard audioRecorder?.record() == true else {
            throw AudioRecorderError.recordingFailed
        }

        isRecording = true

        // Start monitoring audio levels
        startMonitoringLevels()
    }

    func stopRecording() {
        guard isRecording else { return }

        audioRecorder?.stop()
        isRecording = false
        stopMonitoringLevels()
    }

    // MARK: - Audio Level Monitoring
    private func startMonitoringLevels() {
        levelTimer = Timer.scheduledTimer(withTimeInterval: 0.05, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.updateRecordingLevel()
            }
        }
    }

    private func stopMonitoringLevels() {
        levelTimer?.invalidate()
        levelTimer = nil
        recordingLevel = 0.0
    }

    private func updateRecordingLevel() {
        guard let recorder = audioRecorder, isRecording else { return }

        recorder.updateMeters()
        let averagePower = recorder.averagePower(forChannel: 0)

        // Convert dB to linear 0.0-1.0 scale
        // averagePower ranges from -160 (silence) to 0 (max)
        let normalizedLevel = max(0.0, (averagePower + 60.0) / 60.0)
        recordingLevel = normalizedLevel
    }

    // MARK: - Playback
    func playAudio(from url: URL) async throws {
        stopPlaying()

        audioPlayer = try AVAudioPlayer(contentsOf: url)
        audioPlayer?.delegate = self
        audioPlayer?.prepareToPlay()

        guard audioPlayer?.play() == true else {
            throw AudioRecorderError.playbackFailed
        }

        isPlaying = true
    }

    func stopPlaying() {
        audioPlayer?.stop()
        isPlaying = false
    }

    // MARK: - Get Recording
    func getRecordingURL() -> URL? {
        return recordingURL
    }

    func getRecordingData() throws -> Data? {
        guard let url = recordingURL else { return nil }
        return try Data(contentsOf: url)
    }

    // MARK: - Cleanup
    func cleanup() {
        stopRecording()
        stopPlaying()

        // Clean up temporary files
        if let url = recordingURL {
            try? FileManager.default.removeItem(at: url)
        }
    }
}

// MARK: - AVAudioRecorderDelegate
extension AudioRecorder: AVAudioRecorderDelegate {
    nonisolated func audioRecorderDidFinishRecording(_ recorder: AVAudioRecorder, successfully flag: Bool) {
        Task { @MainActor in
            if !flag {
                errorMessage = "Recording failed to complete"
            }
            isRecording = false
        }
    }

    nonisolated func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
        Task { @MainActor in
            errorMessage = error?.localizedDescription ?? "Unknown recording error"
            isRecording = false
        }
    }
}

// MARK: - AVAudioPlayerDelegate
extension AudioRecorder: AVAudioPlayerDelegate {
    nonisolated func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        Task { @MainActor in
            isPlaying = false
        }
    }

    nonisolated func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        Task { @MainActor in
            errorMessage = error?.localizedDescription ?? "Unknown playback error"
            isPlaying = false
        }
    }
}

// MARK: - Errors
enum AudioRecorderError: LocalizedError {
    case permissionDenied
    case invalidURL
    case recordingFailed
    case playbackFailed

    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            return "Microphone permission denied. Please enable it in System Settings."
        case .invalidURL:
            return "Could not create recording file URL."
        case .recordingFailed:
            return "Failed to start recording."
        case .playbackFailed:
            return "Failed to play audio."
        }
    }
}
