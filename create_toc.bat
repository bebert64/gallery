call C:/Users/CassanR/Miniconda3/Scripts/activate
call conda activate shortcuts 
call sphinx-apidoc --force --separate --full -o documentation/source galery
call python documentation/modify_toc.py
call sphinx-build -b html -c documentation documentation/source documentation/build
call conda deactivate