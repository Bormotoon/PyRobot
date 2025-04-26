@echo off
set PATH=%PATH%;C:\Program Files\Java\jdk-24\bin
java -jar tools/antlr-4.13.2-complete.jar -Dlanguage=Python3 pyrobot/backend/kumir_interpreter/grammar/KumirLexer.g4 pyrobot/backend/kumir_interpreter/grammar/KumirParser.g4 -visitor -o pyrobot/backend/kumir_interpreter/generated 