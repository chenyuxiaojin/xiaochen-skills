import Foundation
import Vision
import AppKit
import CoreImage
let args = CommandLine.arguments
let inURL = URL(fileURLWithPath: args[1]); let outPath = args[2]
guard let img = CIImage(contentsOf: inURL) else { print("load fail"); exit(1) }
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: img, options: [:])
try handler.perform([req])
guard let r = req.results?.first else { print("no result"); exit(1) }
let maskPB = try r.generateScaledMaskForImage(forInstances: r.allInstances, from: handler)
let mask = CIImage(cvPixelBuffer: maskPB)
let sx = img.extent.width / mask.extent.width, sy = img.extent.height / mask.extent.height
let maskS = mask.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
let f = CIFilter(name: "CIBlendWithMask")!
f.setValue(img, forKey: kCIInputImageKey)
f.setValue(CIImage(color: CIColor(red:0,green:0,blue:0,alpha:0)).cropped(to: img.extent), forKey: kCIInputBackgroundImageKey)
f.setValue(maskS, forKey: kCIInputMaskImageKey)
let ctx = CIContext()
let out = f.outputImage!.cropped(to: img.extent)
let cs = CGColorSpace(name: CGColorSpace.sRGB)!
try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: outPath), format: .RGBA8, colorSpace: cs, options: [:])
print("ok instances:", r.allInstances.count)
