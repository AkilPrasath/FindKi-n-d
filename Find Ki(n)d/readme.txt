Built using dlib's state-of-the-art face recognition built with deep learning.

Execution Steps:
1. Execute the file "main.py"

Requirements:

Python modules:
	1.face_recognition
	2.dlib
	3.pymongo
	4.numpy
	5.opencv
	6.flask
	
Working of Application:

	link "Found" - pictures of a suspected kid are uploaded here
	link "Lost"  - pictures of lost kids are uploaded here		


Features:

1. Find the face that appear in the picture.
2. Identify the face in picture.

Steps:

1. login
2. Photo of the missing child is uploaded in missing page by the parent.
3. If a lost child is found by public then they can upload the child's photo in the found page.
4. Once the photo has been uploaded in the found page, our algorithm starts to find a match in the database.
5. If there is a match,then a mail is sent to the child's parent along with the geo tags.
	

