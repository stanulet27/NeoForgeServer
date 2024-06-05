#TODO: Update the Dockerfile to include the necessary files
FROM python:latest

ADD test2.py .
ADD Material.py .
ADD Utilities.py .
ADD TestSim.py .

RUN pip install numpy Flask flask-cors 

EXPOSE 5000

CMD ["python", "./test2.py", "./TestSim.py", "Material.py", "Utilities.py"]
