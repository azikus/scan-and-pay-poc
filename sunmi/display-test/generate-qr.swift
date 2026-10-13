import AppKit
import CoreImage
import Vision

let destination = "https://www.azikus.com/scan-and-pay-poc"
let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(Data(destination.utf8), forKey: "inputMessage")
filter.setValue("M", forKey: "inputCorrectionLevel")
let image = filter.outputImage!
let scale: CGFloat = 16
let quietZone: CGFloat = 4
let bounds = image.extent.insetBy(dx: -quietZone, dy: -quietZone)
let white = CIImage(color: CIColor(red: 1, green: 1, blue: 1)).cropped(to: bounds)
let output = image.composited(over: white).transformed(by: CGAffineTransform(scaleX: scale, y: scale))
let cgImage = CIContext(options: [.useSoftwareRenderer: true]).createCGImage(output, from: output.extent)!
let representation = NSBitmapImageRep(cgImage: cgImage)
try representation.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
let request = VNDetectBarcodesRequest()
try VNImageRequestHandler(cgImage: cgImage).perform([request])
guard request.results?.first?.payloadStringValue == destination else {
    fatalError("Generated QR failed destination verification")
}
print("QR generated and decoded: \(destination)")
