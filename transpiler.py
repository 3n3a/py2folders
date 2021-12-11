import os
import argparse
import pprint

cmds = ["print"]
instructions = {
    "commands": {
        "if": 0,
        "while": 1,
        "declare": 2,
        "let": 3,
        "print": 4,
        "input": 5
    },
    "expressions": {
        "variable": 0,
        "add": 1,
        "subtract": 2,
        "multiply": 3,
        "divide": 4,
        "literal_value": 5,
        "equal_to": 6,
        "greater_than": 7,
        "less_than": 8
    },
    "types": {
        "int":0,
        "float":1,
        "string": 2,
        "char": 3
    }
}

# Folder Object
# -----------
# cmd_folder = {"name": "name", "sub":[]}

def createFolders(folder_arr):
    """
    Recursively creates all folders and their subfolders
    """
    for folder in folder_arr:
        parent_path = os.getcwd()
        os.mkdir(folder["name"])
        os.chdir(folder["name"])
        print("Folder "+folder["name"]+" created")
        if len(folder["sub"]) > 0:
            createFolders(folder["sub"])
        os.chdir(parent_path)

def generateFolderNumbers(folder_sub, instruction_type, instruction_type_type):
    j = 0
    while j != instructions[instruction_type][instruction_type_type]:
        j += 1
        folder_sub.append({"name": "folder_"+str(j), "sub": []})
    return folder_sub

def generateFolderValue(folder_sub, content_value):
    content_arr = list(content_value)
    
    i=0
    for val in content_arr:
        i+=1
        folder_sub.append({"name": "hex_"+str(i), "sub": [
            {"name": "part1", "sub":[]},
            {"name": "part2", "sub":[]}
        ]}) 

        byte_chunks = [("0"+[format(x, 'b') for x in bytearray(val, 'utf-8')][0])[i:i+4] for i in range(0, 8, 4)] # converts char to binary & splits chunks of 4

        current_val = folder_sub[i-1]["sub"]
        j=0
        for chunk in byte_chunks:
            j+=1
            bytes = list(chunk)
            h=0
            for byte in bytes:
                h+=1
                current_val[j-1]["sub"].append({"name": "folder_"+str(h), "sub":[]})
                if byte == "1":
                    current_val[j-1]["sub"][h-1]["sub"].append({"name": "one", "sub":[]})
            
    return folder_sub

def generateFolderArr(instructions_arr, program_name):
    folders_arr = [{"name": program_name, "sub": [{}]}]
    folders = folders_arr[0]["sub"][0]
    i = 0
    for instruction in instructions_arr:
        folders["name"] = str(i+1)+"_"+instruction["type"]
        folders["sub"] = [
            {
                "name": "1_Type_Of_Command",
                "sub": []
            },
            {
                "name": "2_Expression",
                "sub": [
                    {
                        "name": "1_Expression_Type",
                        "sub": []
                    },
                    {
                        "name": "2_Content_Type",
                        "sub": []
                    },
                    {
                        "name": "3_Content_Value",
                        "sub": []
                    }
                ]
            }
        ]

        command_type_folder = folders["sub"][0]
        expression_folder = folders["sub"][1]
        cmd_expression = instruction["expression"]

        # Create Folders for Type of Command
        command_type_folder["sub"] = generateFolderNumbers(command_type_folder["sub"], "commands", instruction["type"])

        # Create Folders for Expression.Type
        expression_folder["sub"][0]["sub"] = generateFolderNumbers(expression_folder["sub"][0]["sub"], "expressions", cmd_expression["type"])
        
        # Create Folders for Expression.Content_Type
        expression_folder["sub"][1]["sub"] = generateFolderNumbers(expression_folder["sub"][1]["sub"], "types", cmd_expression["content_type"])

        # Create Folders for Expression.Content_Value
        expression_folder["sub"][2]["sub"] = generateFolderValue(expression_folder["sub"][2]["sub"], cmd_expression["content_value"])

        i+=1
    return folders_arr

class CmdSwitcher():
    def switch(self, cmd, instruction):
        default = "Invalid Command."
        self.instruction = instruction
        return  getattr(self, 'Cmd_'+str(cmd), lambda: default)()

    def Cmd_print(self):
        text2print = self.instruction.split("print")[1].split("(\"")[1].split("\")")[0]
        expression = {
            "type": "literal_value",
            "content_type": "string",
            "content_value": text2print
        }
        command = {
            "type": "print",
            "expression": expression
        }
        return command

def isCommand(cmd, string):
    if string.find(cmd, 0) == 0:
        return True
    else:
        return False

def parseInstructions(instructions):
    cmd_sw = CmdSwitcher()
    parsed_instructions = []
    for i in instructions:
        foundCmd = False
        for cmd in cmds:
            if isCommand(cmd, i):
                foundCmd = True
                parsed_instructions.append(
                    cmd_sw.switch(cmd, i)
                )
                break # jump out of inner for-loop
        if foundCmd == False:
            print("No valid command found for " + i)
    return parsed_instructions

def getInstructions(file):
    f = open(file, "r")
    instructions = f.read().splitlines()        
    return instructions

def transpile(filename):
    instructs = getInstructions(filename)
    parsed_instructs = parseInstructions(instructs)
    folder_arr = generateFolderArr(parsed_instructs, (filename.split(".py")[0]))
    createFolders(folder_arr)
    return folder_arr

def main():
    """
    Main entrypoint
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", help="name of the '.py' program")
    args = parser.parse_args()
    
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(transpile(args.file))


if __name__ == '__main__':
    main()