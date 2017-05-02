DIR := ${CURDIR}
PROGS := cpp_parser.py \
				cpp_lexer.py

all: $(addprefix ${DIR}/src/, ${PROGS})
	@mkdir -p bin/
	@cp $(addprefix ${DIR}/src/, ${PROGS}) ${DIR}/bin/
	@chmod +x $(addprefix ${DIR}/bin/, ${PROGS})
	@echo  "Usage: \n======="
	@echo  "Standalone Lexer: ./bin/cpp_lexer.py ./tests/test1.cpp"
	@echo  "Parser: 	  ./bin/cpp_parser.py ./tests/test1.cpp"
	@echo  "Note: Parser will create 'parse_tree.jpeg' in this directory"
	@chmod +x runcpp
	@echo "RUN executable in the current directory using command : ./runcpp filename"
	@echo "Note: Python version should be at least 3.6.0 or use venv"



clean:
		@rm -f $(addprefix ${DIR}/bin/, ${PROGS} *.pyc __pycache__/*.pyc parser.out parselog.txt parsetab.py)
		@rm -rf bin/
