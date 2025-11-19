//
//  DropZoneView.swift
//  FridgeChef
//
//  Created by Claude on 19/11/2025.
//

import SwiftUI
import AppKit
import UniformTypeIdentifiers

struct DropZoneView: View {
    @Binding var image: NSImage?
    @State private var isTargeted = false

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 16)
                .strokeBorder(
                    style: StrokeStyle(lineWidth: 3, dash: [10])
                )
                .foregroundColor(isTargeted ? .blue : .gray)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(isTargeted ? Color.blue.opacity(0.1) : Color.gray.opacity(0.05))
                )

            if let image = image {
                Image(nsImage: image)
                    .resizable()
                    .scaledToFit()
                    .cornerRadius(12)
                    .padding(8)
            } else {
                VStack(spacing: 16) {
                    Image(systemName: "photo.on.rectangle.angled")
                        .font(.system(size: 64))
                        .foregroundColor(.gray)

                    Text("Drop Fridge Photo Here")
                        .font(.title2)
                        .fontWeight(.medium)

                    Text("or")
                        .foregroundColor(.secondary)

                    Button(action: selectFile) {
                        Label("Select File", systemImage: "folder")
                            .font(.body)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 10)
                    }
                    .buttonStyle(.borderedProminent)

                    Text("Supports: JPG, PNG, HEIC")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .frame(height: 400)
        .onDrop(of: [.image, .fileURL], isTargeted: $isTargeted) { providers in
            handleDrop(providers: providers)
        }
        .overlay(alignment: .topTrailing) {
            if image != nil {
                Button(action: { image = nil }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.white)
                        .background(Circle().fill(Color.black.opacity(0.6)))
                }
                .buttonStyle(.plain)
                .padding(16)
            }
        }
    }

    // MARK: - Drop Handling

    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        guard let provider = providers.first else { return false }

        // Try to load image from provider
        if provider.hasItemConformingToTypeIdentifier(UTType.image.identifier) {
            provider.loadItem(forTypeIdentifier: UTType.image.identifier, options: nil) { (item, error) in
                DispatchQueue.main.async {
                    if let data = item as? Data, let nsImage = NSImage(data: data) {
                        self.image = nsImage
                    } else if let url = item as? URL, let nsImage = NSImage(contentsOf: url) {
                        self.image = nsImage
                    }
                }
            }
            return true
        }

        // Try to load file URL
        if provider.hasItemConformingToTypeIdentifier(UTType.fileURL.identifier) {
            provider.loadItem(forTypeIdentifier: UTType.fileURL.identifier, options: nil) { (item, error) in
                DispatchQueue.main.async {
                    if let data = item as? Data,
                       let url = URL(dataRepresentation: data, relativeTo: nil),
                       let nsImage = NSImage(contentsOf: url) {
                        self.image = nsImage
                    }
                }
            }
            return true
        }

        return false
    }

    // MARK: - File Selection

    private func selectFile() {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false
        panel.canChooseFiles = true
        panel.allowedContentTypes = [.jpeg, .png, .heic, .tiff]
        panel.message = "Select a photo of your fridge"

        if panel.runModal() == .OK, let url = panel.url {
            if let nsImage = NSImage(contentsOf: url) {
                self.image = nsImage
            }
        }
    }
}

// MARK: - Preview

struct DropZoneView_Previews: PreviewProvider {
    static var previews: some View {
        DropZoneView(image: .constant(nil))
            .padding()
            .frame(width: 600, height: 500)
    }
}
