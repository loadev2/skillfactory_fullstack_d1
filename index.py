import sys
import requests

# Данные авторизации в API Trello  
auth_params = {    
    'key': "668d7a3a4713fe3b2ef5fb5865ee2bf6",    
    'token': "0b01601b93753815d9fabe970b6d56bcd22fba0cb19075bccc216259835f1a26", 
    }
  
# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять HTTP запросы.  
base_url = "https://api.trello.com/1/{}"

board_id = "CAUaIdP4"

def read():      
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:          
        # Получим данные всех задач в колонке и перечислим все названия      
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()      
        print("{} ({})".format(column['name'], len(task_data)))
        if not task_data:      
            print('\t' + 'Нет задач!')      
            continue      
        for task in task_data:      
            print('\t' + task['name'])  

def create(name, column_name):      
    # Получим данные всех колонок на доске      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна      
    for column in column_data:      
        if column['name'] == column_name:      
            # Создадим задачу с именем _name_ в найденной колонке      
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break    

def create_list(name):
    url = "https://api.trello.com/1/boards/"+board_id+"/lists"
    query = {'name': name, 'pos': 'bottom', **auth_params}
    response = requests.request("POST", url, params=query)
    print('New list was created. List id is', response.json()["id"])

def move(name, column_name):    
    # Получим данные всех колонок на доске    
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()    
        
    # Среди всех колонок нужно найти задачу по имени и получить её id    
    tasks_arr = []    
    position = 1
    for column in column_data:    
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()    
        for task in column_tasks:   
            if task['name'] == name:  
                tasks_arr.append({
                    'pos':position,
                    'task_id':task['id'],
                    'name':task['name'],
                    'column':column['name']})  
                position+=1  

    if not len(tasks_arr):
        print('Task has not been found')
        return
    
    updated_task = tasks_arr[0]

    if len(tasks_arr) > 1:
        for task in tasks_arr:
            print("{}: {} ({})".format(task['pos'],task['name'],task['column']))
        pos_task = input('You have more then 1 task with this name. Please enter position of your task: ')
        if int(pos_task)>0 and int(pos_task)<=len(tasks_arr):
            updated_task = tasks_arr[int(pos_task)-1]
        else:
            print('Invalid number has been chosen')
            return

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить    
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу    
    for column in column_data:    
        if column['name'] == column_name:    
            # И выполним запрос к API для перемещения задачи в нужную колонку    
            requests.put(base_url.format('cards') + '/' + updated_task['task_id'] + '/idList', data={'value': column['id'], **auth_params})    
            break      	

if __name__ == "__main__":    
    if len(sys.argv) <= 2:      
        read()      
    elif sys.argv[1] == 'create':    
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_list(sys.argv[2])    
    elif sys.argv[1] == 'move':    
        move(sys.argv[2], sys.argv[3]) 