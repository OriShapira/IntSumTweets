# Interactive Abstractive Summarization Generation based on "Open Knowledge Representation" Structures

This code generates an interactive summary of a set of tweets.
The input is an OKR structure (which can be created with: https://github.com/vered1986/OKR/tree/props).
The output is a json which can then be used by other applications such as the backend server of the online demo application.

The original paper can be found in: https://aclanthology.org/D17-2019.pdf

The code here is not the exact code used in the paper.

The OKR paper can be found in: https://aclanthology.org/W17-0902.pdf

### Content

The src/Generation folder contains the code for generating the summary.

The src/Application folder contains the code for the website which presents the interactive summary.

The requirements.txt file is for installing the proper python dependencies.

### Setting up ###

* Prepare the code:
	* Clone the repository
	* Install dependenices (listed in the requirements.txt file)
		* In Linux, you can create a virtalenv and pip install the requirments file		
* Create the interactive summary:
	* Prepare input OKR json files (see OKR repo), or use the examples. The names must end with the extension '.in.json'.
	* Run: python src/Generation/Main.py examples/json -new -json examples/json/out
* Prepare the application environment:
	* In your web server root, create a folder for the frontend and copy there the frontend files.
	* In your backend location, create a folder for the backend and copy there the backend files.
	* In the frontend file app/pages/pages.module.js, make sure the base url points to the correct location. Examples:
		* $rootScope.baseUrl = "http://localhost:1379/";
		* $rootScope.baseUrl = "http://your-server/whatever/";
* View the interactive summary:
	* Copy the output jsons to the appServer/db/jsonsMains directory where the server is located
	* The json filename <storyName>.json corresponds to the string used in the appServer/db/userStudies.txt "story" key value (i.e. 'story': 'storyName').
	* Copy the jsons also to appServer/db/jsonsBaselines2 and change the string "dynamicStoryScreenInput" to "baseline2ScreenInput".
	* To see the story in the UI from the file �storyName.json�:
		* Add a user "demoXYZ" in a new line in appServer/db/users.txt (e.g. demoSmile;;;password;;;null)
		* In appServer/db/userStudies.txt add a line: demoSmile;;;[{'done': False, 'story': 'storyName', 'steps': [(MAIN, -1)]}]
		* Login to the system (e.g. http://127.0.0.1/okr/) with user demoSmile and the password set.
		 (Because the username starts with the string "demo", you will be able to see it every time it is entered, and without inputing the registration data after the first entrance.)
		 
### Citing ###
If any resource from this repository is used, please cite:
```
@inproceedings{shapira-etal-2017-interactive,
    title = "Interactive Abstractive Summarization for Event News Tweets",
    author = "Shapira, Ori  and
      Ronen, Hadar  and
      Adler, Meni  and
      Amsterdamer, Yael  and
      Bar-Ilan, Judit  and
      Dagan, Ido",
    booktitle = "Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    month = sep,
    year = "2017",
    address = "Copenhagen, Denmark",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/D17-2019",
    doi = "10.18653/v1/D17-2019",
    pages = "109--114",
}
```