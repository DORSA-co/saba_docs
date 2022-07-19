DEBUG=False

class moveOnList:
    

    def __init__(self):

        self.lists={}
        self.idxs={}

    def add(self, mylist, name):
        self.lists[name] = mylist
        self.idxs [name] = 0

    
    def check(self,name):
        if name in self.lists.keys():
            return True
        return False

    def build_next_func(self, name):   
        def next_on_list():
            self.idxs[name]+=1
            self.idxs[name]=min(self.idxs[name],len(self.lists[name])-1)

            if DEBUG:
                print("*"*50,self.idxs[name],len(self.lists[name]))
        return next_on_list


    def build_prev_func(self, name):  
        def prev_on_list():
            self.idxs[name]-=1
            self.idxs[name]=max(self.idxs[name],0)
            
            if DEBUG:
                print("*"*50,self.idxs[name],len(self.lists[name]))

        return prev_on_list


    
    def next_on_list(self,name):
        self.idxs[name]+=1
        #self.idxs[name]=min(self.idxs[name],len(self.lists[name])-1)
        if self.idxs[name] >= len(self.lists[name]) :
            self.idxs[name] = 0

        if DEBUG:
            print("*"*50,self.idxs[name],len(self.lists[name]))


    def prev_on_list(self,name):
        self.idxs[name]-=1
        #self.idxs[name]=max(self.idxs[name],0)
        if self.idxs[name] < 0:
            self.idxs[name] = len(self.lists[name])-1

        if DEBUG:
            print("*"*50,self.idxs[name],len(self.lists[name]))






    def get_current(self,name):
        mylist = self.lists[ name ] 
        idx = self.idxs[name]
        return mylist[idx]

    def get_list(self,name):
        mylist = self.lists[ name ] 
        return mylist

    def get_count(self,name):
        mylist = self.lists[ name ] 
        return len( mylist )




if __name__ == '__main__':
    l = ['a1', 'a2', 'a3', 33, 'a4', 'a5']
    obj = moveOnList()
    obj.add(l,'coils')

    next_f = obj.build_next_func('coils')
    prev_f = obj.build_prev_func('coils')
    
    next_f()
    next_f()
    next_f()
    prev_f()
    print(obj.get_current('coils'))