from reprint import output
import time

filenames = [
'File_1',
'SomeFileWithAVeryLongNameWhichMakeitToANewLineWhichMayInfluenceTheReprintModuleButActuallyNot.exe',
'File_3',
'File_4',
]

if __name__ == "__main__":
    with output(output_type='dict') as output_lines:
        for i in range(4):
            output_lines['Moving file'] = filenames[i]

            if i == 1 or i == 2:
                output_lines['tmp'] = 'this is tmp'
            else:
                if 'tmp' in output_lines:
                    output_lines.pop('tmp')
                    
            for progress in range(100):
                output_lines['Total Progress'] = "[{done}{padding}] {percent}%".format(
                    done = "#" * int(progress/10),
                    padding = " " * (10 - int(progress/10)),
                    percent = progress
                    )
                time.sleep(0.02)
            
                
                