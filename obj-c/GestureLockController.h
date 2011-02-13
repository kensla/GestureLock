#import <Cocoa/Cocoa.h>
#import <QTKit/QTkit.h>

@interface GestureLockController : NSObject {
  IBOutlet QTCaptureView *mCaptureView;
    
  QTCaptureSession            *mCaptureSession;
  QTCaptureVideoPreviewOutput *mCaptureVideoOutput;
  QTCaptureDeviceInput        *mCaptureVideoDeviceInput;
  QTCaptureDeviceInput        *mCaptureAudioDeviceInput;
}
- (IBAction)startRecording:(id)sender;
- (IBAction)stopRecording:(id)sender;

@end
