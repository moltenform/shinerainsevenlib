# shinerainsevenlib (Ben Fisher, moltenform.com)
# Released under the LGPLv2 License


class Default:
    "Use with function parameters to see if a value was passed, or left to default"

    def __repr__(self):
        return 'DefaultValue'


DefaultVal = Default()
