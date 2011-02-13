#import "GestureLockController.h"

@implementation GestureLockController

- (void)awakeFromNib
{
    
// Create the capture session
    
	mCaptureSession = [[QTCaptureSession alloc] init];
    
// Connect inputs and outputs to the session	
    
	BOOL success = NO;
	NSError *error;
	
// Find a video device  
    
    QTCaptureDevice *videoDevice = [QTCaptureDevice defaultInputDeviceWithMediaType:QTMediaTypeVideo];
    success = [videoDevice open:&error];
    
    
// If a video input device can't be found or opened, try to find and open a muxed input device
    
	if (!success) {
		videoDevice = [QTCaptureDevice defaultInputDeviceWithMediaType:QTMediaTypeMuxed];
		success = [videoDevice open:&error];
		
    }
    
    if (!success) {
        videoDevice = nil;
        // Handle error
        
    }
    
    if (videoDevice) {
//Add the video device to the session as a device input
		
		mCaptureVideoDeviceInput = [[QTCaptureDeviceInput alloc] initWithDevice:videoDevice];
		success = [mCaptureSession addInput:mCaptureVideoDeviceInput error:&error];
		if (!success) {
			// Handle error
		}
        
// If the video device doesn't also supply audio, add an audio device input to the session
        
        if (![videoDevice hasMediaType:QTMediaTypeSound] && ![videoDevice hasMediaType:QTMediaTypeMuxed]) {
            
            QTCaptureDevice *audioDevice = [QTCaptureDevice defaultInputDeviceWithMediaType:QTMediaTypeSound];
            success = [audioDevice open:&error];
            
            if (!success) {
                audioDevice = nil;
                // Handle error
            }
            
            if (audioDevice) {
                mCaptureAudioDeviceInput = [[QTCaptureDeviceInput alloc] initWithDevice:audioDevice];
                
                success = [mCaptureSession addInput:mCaptureAudioDeviceInput error:&error];
                if (!success) {
                    // Handle error
                }
            }
        }
        
// Create a video preview output and add it to the session

      mCaptureVideoOutput = [[QTCaptureVideoPreviewOutput alloc] init];
      success = [mCaptureSession addOutput:mCaptureVideoOutput error:&error];
      if (!success) {
        NSLog(@"Add Decompressed Video Output failed.");
      }
      [mCaptureVideoOutput setDelegate: self];


      
	NSEnumerator *connectionEnumerator = [[mCaptureVideoOutput connections] objectEnumerator];
	QTCaptureConnection *connection;
	
	// iterate over each output connection for the capture session
	while ((connection = [connectionEnumerator nextObject])) {
		NSString *mediaType = [connection mediaType];

    /* if the type of connected media is video */
		if ([mediaType isEqualToString:QTMediaTypeVideo]) {
    }
    
  } 

// Associate the capture view in the UI with the session
        
        [mCaptureView setCaptureSession:mCaptureSession];
        
        [mCaptureSession startRunning];
        
	}
    
}

// Handle window closing notifications for your device input

- (void)windowWillClose:(NSNotification *)notification
{
	
	[mCaptureSession stopRunning];
    
    if ([[mCaptureVideoDeviceInput device] isOpen])
        [[mCaptureVideoDeviceInput device] close];
    
    if ([[mCaptureAudioDeviceInput device] isOpen])
        [[mCaptureAudioDeviceInput device] close];
    
}

// Handle deallocation of memory for your capture objects

- (void)dealloc
{
	[mCaptureSession release];
	[mCaptureVideoDeviceInput release];
  [mCaptureAudioDeviceInput release];
	[mCaptureVideoOutput release];
	[super dealloc];
}

#pragma mark-

// Add these start and stop recording actions, and specify the output destination for your recorded media. The output is a QuickTime movie.

- (IBAction)startRecording:(id)sender
{
	//[mCaptureMovieFileOutput recordToOutputFileURL:[NSURL fileURLWithPath:@"/Users/Shared/My Recorded Movie.mov"]];
}

- (IBAction)stopRecording:(id)sender
{
	//[mCaptureMovieFileOutput recordToOutputFileURL:nil];
}

- (void)captureOutput:(QTCaptureOutput *)captureOutput 
  didOutputVideoFrame:(CVImageBufferRef)videoFrame 
     withSampleBuffer:(QTSampleBuffer *)sampleBuffer 
       fromConnection:(QTCaptureConnection *)connection
{
  NSLog(@"capture called back");
  CIImage *img = [CIImage imageWithCVImageBuffer: videoFrame];
  NSBitmapImageRep *bmp = [[NSBitmapImageRep alloc] initWithCIImage: img];
  
  NSUInteger rgb[] = {0,0,0,0};
  [bmp getPixel:rgb atX:0 y:0];
  NSLog(@"isplanar? %d", [bmp isPlanar]);
  NSLog(@"sample per pixel: %d", [bmp samplesPerPixel]);
  NSLog(@"bytesPerRow: %d", [bmp bytesPerRow]);
  NSLog(@"width: %d", [bmp bytesPerRow]/[bmp samplesPerPixel]);
  NSLog(@"height: %d", [bmp bytesPerPlane]/[bmp bytesPerRow]);
  //NSLog(@"pixel at 0,0: (%d, %d, %d, %d)", rgb[0], rgb[1], rgb[2], rgb[3]);   
        
  [bmp release];
}
@end
