# Creeper

This is a modular crawler framework that can adapt to different websites for downloading as much as possible.

**ATTENTION**: This framework is for learning purposes only and should not be applied to any commercial scenarios or any possible illegal activities. If there is illegal use, the author is not responsible for any consequences caused by such behavior. All consequences shall be borne by the user.

This module implements a crawler for downloading questions from zujuan.xkw.com. We found that zujuan.xkw.com has a very strict limit on daily traffic, with a maximum daily traffic of approximately 900 for the server used to return parsed images. This is not good news. Therefore, in order to minimize access to the server as much as possible, we save the webpage in mhhtml format to preserve the image information inside. This ensures that each parsed image will only be accessed once. This increases the number of questions that can be obtained daily.

For the obtained questions, the following modules can be sequentially called for parsing:

Please refer to the specific program for the relevant parameter settings and usage instructions.