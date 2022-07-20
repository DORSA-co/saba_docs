DEBUG=False


class moveOnList:
    """
    this function is used to create a list of elements, with option to go next or preivious on list and
    get current objet/element

    :returns: moveOnList class
    """

    def __init__(self):
        self.lists={} # dict of lists, there can be multiple lists added, each one with a name (key)
        self.idxs={} # dict of current index, each for one list. its the current index for each list


    def add(self, mylist, name):
        """
        this function is used to add a list or elements with name/key

        :param mylist: (_type_) _description_
        :param name: (_type_) name of list
        
        :returns: None
        """

        self.lists[name] = mylist
        self.idxs[name] = 0

    
    def check(self, name):
        """
        this function is used to check if a key/name is in class

        :param name: (_type_): input name

        :returns: resault: boolean detetmining if the name if avilable
        """

        if name in self.lists.keys():
            return True
        return False


    def build_next_func(self, name):
        """
        this function is used to get a next object fot moving nect on a list

        :param name: (_type_) name/key of list
        
        :returns: next_on_list oject
        """

        def next_on_list():
            self.idxs[name]+=1
            self.idxs[name]=min(self.idxs[name],len(self.lists[name])-1)

            if DEBUG:
                print("*"*50,self.idxs[name],len(self.lists[name]))
        return next_on_list


    def build_prev_func(self, name): 
        """
        this function is used to get a previous object fot moving nect on a list

        :param name: (_type_) name/key of list
        
        :returns: prev_on_list oject
        """

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
        """
        this function is used to get curent element in a list

        :param name: (_type_) name/key of list

        :returns: current_element of list:
        """

        mylist = self.lists[ name ] 
        idx = self.idxs[name]
        return mylist[idx]


    def get_list(self,name):
        """
        this function is used to get a list using its name/key

        :param name: (_type_) name/key of list

        :returns: list: _description_
        """

        mylist = self.lists[name] 
        return mylist


    def get_count(self,name):
        """
        this function is used to get count of elements in a list

        :param name: (_type_) name/key of list

        :returns: len_list: _description_

        """
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