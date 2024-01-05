#set base image host
FROM python:3.8


#set working directory in container
WORKDIR /src

#install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.11.0/ncbi-blast-2.11.0+-x64-linux.tar.gz
COPY blastp/ncbi-blast-2.11.0+-x64-linux.tar.gz .
RUN tar -zxvf ncbi-blast-2.11.0+-x64-linux.tar.gz
ENV PATH /src/ncbi-blast-2.11.0+/bin:$PATH

#copy required code and database files
COPY cluster_function_prediction.py .
COPY cluster_function_prediction_tools.py .
COPY readFeatureFiles.py .
COPY readInputFiles.py .
COPY SSN_tools.py .
COPY rank_features_as5.py .
# COPY *.py . # requires a destination directory
COPY cluster_list.csv .
RUN mkdir feature_matrices/
RUN mkdir SSN/
RUN mkdir /src/temp_file/
COPY feature_matrices/ ./feature_matrices/
COPY SSN/ ./SSN/

#make script executable
RUN chmod +x /src/cluster_function_prediction.py

#set up working directory for input and output
RUN chmod 777 /src  
RUN chmod 777 /src/temp_file/
ENV PATH /src:$PATH
USER 1000:1000
ENTRYPOINT  ["python", "/src/cluster_function_prediction.py"]
CMD ["--help"]