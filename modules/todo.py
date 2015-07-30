

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("todo").hook(
            self.todo, help="Read and modify your todo list")
    
    def get_todo(self, server, nickname):
        return server.config.get("users", {}).get(nickname.lower(),
            {}).get("todo", [])
    
    def add_todo(self, server, nickname, todo):
        with server.config as config:
            if not "users" in config:
                config["users"] = {}
            if not nickname.lower() in config["users"]:
                config["users"][nickname.lower()] = {}
            if not "todo" in config["users"][nickname.lower()]:
                config["users"][nickname.lower()]["todo"] = []
            config["users"][nickname.lower()]["todo"].append(todo)
    
    def del_todo(self, server, nickname, n):
        todo = self.get_todo(server, nickname)
        if len(todo) > n:
            todo.pop(n)
            if not todo:
                del server.config["users"][nickname.lower()]["todo"]
            return True
        return False
    
    def todo(self, event):
        if event["args_split"]:
            if event["args_split"][0].lower() == "add":
                todo = " ".join(event["args_split"][1:])
                if not todo:
                    return "Please supply a description."
                self.add_todo(event["server"], event["sender"].nickname,
                    todo)
                return "Saved."
            elif event["args_split"][0].lower() == "del":
                if not len(event["args_split"]) > 1:
                    return "Please supply the number of the todo item to delete."
                if not event["args_split"][1].isdigit():
                    return "That's not a number."
                n = int(event["args_split"][1])
                if not n > 0:
                    return "Please supply a positive number."
                if self.del_todo(event["server"], event["sender"
                        ].nickname, n-1):
                    return "Deleted todo item."
                else:
                    return "You do not have that many things in your todo."
            elif event["args_split"][0].isdigit():
                todo = self.get_todo(event["server"], event["sender"
                    ].nickname)
                n = int(event["args_split"][0])
                if not n > 0:
                    return "Please supply a positive number."
                if len(todo) > n-1:
                    return "%d: %s" % (n, todo[n-1])
                else:
                    return "You do not have that many things in your todo."
            else:
                return "Unknown argument."
        else:
            todo = self.get_todo(event["server"], event["sender"].nickname)
            if todo:
                return "You have %d items in your todo." % len(todo)
            else:
                return "You have nothing in your todo."