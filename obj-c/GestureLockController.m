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
        
// Create the movie file output and add it to the session
        
        mCaptureMovieFileOutput = [[QTCaptureMovieFileOutput alloc] init];
        success = [mCaptureSession addOutput:mCaptureMovieFileOutput error:&error];
        if (!success) {
            // Handle error
        }
        
        [mCaptureMovieFileOutput setDelegate:self];


// Set the compression for the audio/video that is recorded to the hard disk.

	NSEnumerator *connectionEnumerator = [[mCaptureMovieFileOutput connections] objectEnumerator];
	QTCaptureConnection *connection;
	
	// iterate over each output connection for the capture session and specify the desired compression
	while ((connection = [connectionEnumerator nextObject])) {
		NSString *mediaType = [connection mediaType];
		QTCompressionOptions *compressionOptions = nil;
		// specify the video compression options
		// (note: a list of other valid compression types can be found in the QTCompressionOptions.h interface file)
		if ([mediaType isEqualToString:QTMediaTypeVideo]) {
			// use H.264
			compressionOptions = [QTCompressionOptions compressionOptionsWithIdentifier:@"QTCompressionOptions240SizeH264Video"];
		// specify the audio compression options
		} else if ([mediaType isEqualToString:QTMediaTypeSound]) {
			// use AAC Audio
			compressionOptions = [QTCompressionOptions compressionOptionsWithIdentifier:@"QTCompressionOptionsHighQualityAACAudio"];
		}
		
		// set the compression options for the movie file output
		[mCaptureMovieFileOutput setCompressionOptions:compressionOptions forConnection:connection];
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
	[mCaptureMovieFileOutput release];
	
	[super dealloc];
}

#pragma mark-

// Add these start and stop recording actions, and specify the output destination for your recorded media. The output is a QuickTime movie.

- (IBAction)startRecording:(id)sender
{
	[mCaptureMovieFileOutput recordToOutputFileURL:[NSURL fileURLWithPath:@"/Users/Shared/My Recorded Movie.mov"]];
}

- (IBAction)stopRecording:(id)sender
{
	[mCaptureMovieFileOutput recordToOutputFileURL:nil];
}

// Do something with your QuickTime movie at the path you've specified at /Users/Shared/My Recorded Movie.mov"

- (void)captureOutput:(QTCaptureFileOutput *)captureOutput didFinishRecordingToOutputFileAtURL:(NSURL *)outputFileURL forConnections:(NSArray *)connections dueToError:(NSError *)error
{
	[[NSWorkspace sharedWorkspace] openURL:outputFileURL];
}


@end
