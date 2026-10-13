# Automatic document capture — 13 October 2026

Markus requested Apple-native document detection, a grey mask outside the paper, automatic camera capture and integration with the existing Adjust image flow.

## Flow

The camera now uses Apple's on-device Vision `VNDetectDocumentSegmentationRequest` on live frames. A grey preview mask excludes the detected quadrilateral, leaving paper pixels unobscured. The mask follows the aspect-fit camera image, including letterboxing and Vision's bottom-left coordinate origin. Native `VNDocumentCameraViewController` owns its UI and returns pages after Save; Vision was selected to support the requested custom mask and direct transition within the existing branded flow.

When document segmentation does not find a safely framed page, Apple's `VNDetectRectanglesRequest` checks for an interior rectangle with confidence of at least 0.8. The largest eligible rectangle is used. This handles plain-paper scenes where segmentation returns the frame boundary; the native synthetic-image test reproduced that case before the fallback was added. Both paths use the same stability and full-frame bounds checks.

**Auto** is enabled initially. Capture requires all four edges inside the frame, at least 18% image area, confidence of at least 0.6, five observations over at least 0.9 seconds, and no corner moving more than 1.8% of the frame from the initial steady position. Missing/low-confidence/clipped paper, movement and a gap longer than 0.45 seconds restart the wait. Detection is throttled to at most one request every 0.18 seconds; late camera frames are discarded. This is a usability heuristic, not evidence that payment details are correct.

The app takes a full-resolution still once per camera run. It detects the paper again in that still rather than applying live-video coordinates to a different photo field of view. Core Image `CIPerspectiveCorrection` straightens it with a small edge margin. If the still cannot be safely detected or corrected, the complete photo opens for manual adjustment instead. There is no contrast/binarization filter or OCR in this capture step.

The resulting image opens **Adjust image**, with existing crop handles, Rotate, Reset crop, Retake, Use crop and Edit crop. The full camera photo remains in memory alongside the rectified image. **Reset crop** restores it, retaining any rotation applied in the adjustment screen; **Edit crop** also starts from the complete photo. This allows correcting a bad automatic boundary without losing payment details. A manual shutter/import uses the complete original photo as before. The preview mask is never baked into the image. Only explicit **Send** prepares/uploads the chosen image. Review, confirmation, frozen recovery, hotspot settings, dark glass and the existing SUNMI lifecycle observer remain intact.

The shutter remains available as a fallback; **Auto / Manual** pauses automatic capture. Import is retained. Camera work stops when Connection settings, the photo picker or completion is open, and while loading an import or backgrounded. Lifetime checks discard late detections/photos after leaving capture. Retake/reset starts a fresh stability wait. Detection failure leaves manual capture/import available.

## Verification

Branch `codex/ios-auto-document-scan` starts from freshly fetched main `269e022` (merged PR #11), in `/Users/markusi/.codex/worktrees/ios-auto-document-scan/scan-and-pay`. It includes the latest country-aware extraction, invoice applicability, dark mode and SUNMI lifecycle telemetry. The initial implementation was moved out of the old original checkout; unrelated untracked SUNMI files remain untouched. A private backup of that initial source is retained with the evidence.

Final verification on iOS 26.2: **39 native unit/recovery tests and all four existing UI flows passed** (43 total, zero failures). Seven scanning tests cover one-shot stability and rearming, drift/loss/frame gaps, clipped/small/low-confidence paper, preview coordinate mapping, correction orientation, full-photo preservation and the crop/edit/reset handoff without Send. The actual Apple detector also runs on a synthetic paper image; its mask and corrected-image attachments were visually inspected. The earlier failed segmentation-only test is retained in `combined-tests.xcresult`; the fixed final run is `final-tests.xcresult`. Swift formatting and diff checks pass.

The combined signed iPhone build passed and was installed in place on the previously paired iPhone 16 Pro, preserving existing app data. Markus subsequently confirmed that the new camera flow works on the physical device. This is user acceptance, separate from the measured simulator checks and the previously accepted overall mobile/SUNMI integration.

Private evidence is under the original checkout's `.local/document-scan-2026-10-13/`: final build/test logs, synthetic image attachments, and device installation/launch results. No paid extraction, backend restart, private configuration/selection change or scan/payment confirmation was performed by the agent.

## Subsequent local backend outage

After camera acceptance, Markus reported `Profile execution failed; diagnostic contents are private.` The two latest failed jobs had no provider stage or raw response; both predated installation of this camera update. The running server referenced the removed invoice-context worktree, and admin logs confirmed missing source assets. The generic extraction exception did not retain a traceback, so its exact failing instruction cannot be established retrospectively.

During investigation, the separately authorized website chat restored the backend from a stable Git archive of merged main `269e0223580ecba96793d9382c3efcffa77d720e`, under the original checkout's ignored `.local/runtime-source/` directory, and restarted it while idle. The existing private launcher now points there. Worktree cleanup no longer removes that runtime's source. Historical instructions to retain the invoice-context worktree are superseded by this deployment.

Independent verification passed: authenticated health/profile/catalogue reads, admin/display serving, request preparation for the exact selected OpenAI profile, and 108 offline extended-adapter/invoice-context tests from the deployed source. Jobs, accounting, stages, reviews, selection and backend identity match the pre-restart snapshot. No provider request or failed-job retry was made during verification. Markus subsequently confirmed on 13 October that explicit phone Send works after the repair. This closes the live verification gate through user confirmation; no additional agent run or timing measurement is claimed. Retained failures remain unchanged.

## Apple references

- [Native document detection](https://developer.apple.com/documentation/vision/vndetectdocumentsegmentationrequest)
- [Vision rectangle observations](https://developer.apple.com/documentation/vision/vnrectangleobservation)
- [Native scanner controller](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [Core Image perspective correction](https://developer.apple.com/documentation/coreimage/ciperspectivecorrection)
