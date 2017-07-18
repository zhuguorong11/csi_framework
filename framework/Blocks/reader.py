import time, os

file = open('csi_test.dat') 
file1 = open('csi_test1.dat', 'w') 

while 1:
   where = file.tell()
   line = file.readline() 
   if not line: 
      time.sleep(1) 
      file.seek(where) 
   else:
      print(line)
      # This is where the file gets broadcasted.
      file1.write(line)
      file1.flush() 
      os.fsync(file1.fileno())  
