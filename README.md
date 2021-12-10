# Project_TeamT_CSC322
GradSchoolZero is a fictitious college where both students and instructors can apply. 
During different semester periods, students will be able to enroll in classes taught by various professors, receive grades, write reviews, and more!

## Instructions To Run On Your Computer
1. Create a python virtual environment
2. ```Shell
    pip install -r requirements.txt
    ```
3. Set environment variables on your computer:
    - `EMAIL_ADDR` to your email address
    - `EMAIL_PASS` to your email password. May have to be app password if using 2FA
    - `REGISTRAR_PASS` to a password of your choice. This will be password for registrar login.
    
    Please note that the automated email feature is set to work with gmail. If you would like to use a different email provider, adjust lines 14 and 15 in `__init__.py`. Otherwise, there will be an error when the program tries to send an email. 

    [How to set environment variable in Mac & Linux](https://www.youtube.com/watch?v=5iWhQWVXosU&t=51s)
    
    [How to set environment variable in Windows](https://www.youtube.com/watch?v=IolxqkL7cD8)

    If there is an error where the environment variables are empty, try restarting your computer. It works for me (on windows at least).
4. ```Shell
    cd flask
    py run.py
    ```

