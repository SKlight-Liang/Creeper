# Creeper

This is a modular crawler framework that can adapt to different websites for downloading as much as possible.

**ATTENTION**: This framework is for learning purposes only and should not be applied to any commercial scenarios or any possible illegal activities. If there is illegal use, the author is not responsible for any consequences caused by such behavior. All consequences shall be borne by the user.

This module implements a crawler for downloading images from Shutterstock.com.
It evaded the website's crawler inspection program by simulating the behavior of the browser.
Unfortunately, we still need to perform a human-machine verification every time we open it.
At present, no effective method has been found to avoid this authentication system.
This may be because it detected extremely fast access requests.
The good news is that this inspection is only done once, 
and there is no need for any human-machine verification afterwards.
Okay, this may be a minor oversight.
We have to admit that its anti crawling technology is very excellent.

We provide the following methods:
- `ShutterStock.py`: The main crawling module 
- `SimilarImage.py`: The similar image search engine based on Shutterstock API

Please refer to the specific program for the relevant parameter settings and usage instructions.