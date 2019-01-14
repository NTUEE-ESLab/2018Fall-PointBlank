CC = gcc
CFLAGS  = -Wall
LFLAGS  = -lm 
SrcType = c
SrcDir  = ./
ObjDir  = obj/
BinDir  = bin/
Srcs   := $(notdir $(wildcard $(SrcDir)*.$(SrcType)))
Objs   := $(Srcs:%.$(SrcType)=%.o)
Bin     = dmp

.PHONY  = all objdir bindir clean run
 
all: objdir bindir $(BinDir)$(Bin)

objdir:
ifeq ("$(wildcard $(ObjDir))", "")
	mkdir $(ObjDir)
endif

bindir:
ifeq ("$(wildcard $(BinDir))", "")
	mkdir $(BinDir)
endif

clean: 
	-rm $(BinDir)$(Bin)
	-rm $(addprefix $(ObjDir), $(Objs))

$(BinDir)$(Bin): $(addprefix $(ObjDir), $(Objs))
	$(CC) -o $@ $^ $(LFLAGS)

$(ObjDir)%.o: $(SrcDir)%.$(SrcType)
	$(CC) $(CFLAGS) -o $@ -c $<