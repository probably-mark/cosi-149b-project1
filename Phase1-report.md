Authors: MyongJoon Chang, Mark McAvoy, Eurey Noguchi
Date: February 20, 2019

During phase1 of our project our group started with the OpenCV Text Detection model, along with the frozen_east_text_detection pretrained model for text detection.  Running through the program, we realized that there were large amounts of false positives where the EAST model would be detecting object which would look like text. The most common one was piping on the ceiling which the model could have mistaken as resembling “1111”.  

After, tweaking and taking only the essential parts of the video searching model and adding to it our own python code we managed to print out text that was getting detected. However, once we started printing out text we realized that the EAST model was essentially only a text detector. The EAST model was recognizing that there was text on the door signs however was not actually recognizing the actual wording. Therefore, we used Tesseract to change the model so that the model would be recognizing the text in the bounded boxes that was provided by the EAST model.

These were the main problems that we tried to tackle during phase 1. We managed to filter out much of the noise to get rid of the false positives and make our model only focus on the room sign and only display the room number. However, during this process, we realized that we also managed to create false negatives. Our model only recognized some door signs, however for the door signs that it recognized it would be predicting the number quite accurately.

Also during the exporting of the video files which should contain boxes of the images found, the files seems to be getting corrupted during the process, therefore making it hard to open and/or recognize the changes that occured. 

During phase 2 of our project we plan on trying a different approach, instead of using a pretrained model, our plan is training our own model and would recognize door signs as an object. Originally, we had tried this approach by using Keras to train a CNN that would be able to differentiate between door signs and other objects. However, the problem that we realized was that this model is not compatible with our existing code, there would make our work in phase 1 ineffective. Therefore, this would require us to find another video parsing model that would be able to use the CNN created and trained using Keras.

Therefore, we changed our plan to use the TensorFlow Object Detection API to make a model that would only recognize door signs. First off this would be quite compatible with our existing model and would effectively get rid of all false positives and not create any false negatives that is currently happening. However, this would require certain extra work from our side. First, we would need to take photos of door signs and then annotate the images so the TensorFlow API could be trained using these models. 

Our plan would be then to test this new frozen_model on the given video’s and see how accurately it can recognize the door signs.  Along with this it would be possible to annotate the training video’s and use the videos as additional training samples.  If everything goes as planned this would make it possible for us to get rid of all false positives and false negatives and create a model which would be much more accurate.

If time allow, we would also like to find a way to increase the fps of the current program since the current fps is quite low. 
