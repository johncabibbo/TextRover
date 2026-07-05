==========================================================================================
⏺ TextRover 
==========================================================================================

	Location: ~/Documents/script/textRover/                                                           
	                                                                                                
	Files:                                                                                    
	┌──────────────────────┬────────────────────────────────┐                                         
	│         File         │          Description           │                                         
	├──────────────────────┼────────────────────────────────┤                                         
	│ textRover.py         │ Main script (32KB, executable) │                                         
	├──────────────────────┼────────────────────────────────┤                                         
	│ textRoverConfig.json │ Configuration file             │                                         
	├──────────────────────┼────────────────────────────────┤                                         
	│ README.md            │ Full documentation             │                                         
	└──────────────────────┴────────────────────────────────┘                                         
	---                                                                                               
	Configuration Options in textRoverConfig.json:                                                    
	                                                                                                
	{                                                                                                 
	  "interactiveMode": false,     // Set true to ignore config and prompt for everything          
	  "searchFolder": "~/...",      // Folder to search recursively                                 
	  "searchPattern": "TODO",      // Text or regex pattern                                        
	  "isRegex": false,             // Treat pattern as regex                                       
	  "caseSensitive": true,        // Case-sensitive matching                                      
	  "fileExtensions": [".txt", ".js", ".sh", ".inc", ".php", ".py"],                              
	  "action": "display",          // display | write | replace | replace_line                     
	  "outputFile": "...",          // For 'write' action                                           
	  "replaceWith": "",            // For 'replace' action                                         
	  "replaceLine": "",            // For 'replace_line' action                                    
	  "dryRun": true,               // Preview without changes                                      
	  "createBackup": true,         // Create .bak before modifying                                 
	  "backupExtension": ".bak"     // Backup file extension                                        
	}                                                                                                 
	                                                                                                
	---                                                                                               
	Run it:                                                                                           
	                                                                                                
	# Interactive mode (prompts for everything)                                                       
	python3 ~/Documents/script/textRover/textRover.py -i                                              
	                                                                                                
	# From config file                                                                                
	python3 ~/Documents/script/textRover/textRover.py -c                                              
	                                                                                                
	# Main menu                                                                                       
	python3 ~/Documents/script/textRover/textRover.py                                                 
	                                                                                                
	The script follows CB9Lib standards with the proper header format, menu styling, colors, and exit 
	screen as shown in your reference screenshots.          

	❯ In the readme file provide examples for text searches for these:                                  
	  1. abc{*}def - Find abc followed by up to 500 chars then def, case insensitive                    
	  2. abc - Find abd with any text before or after, case insensitive                                 
	  3. abc{*10}def - Find abc with up to 10 chars, then def, case insensitive                         
	  4. ab{*2!}def - Find ab, then exactly 2 chars, then def, case insensitive                         
	  5. [ABc] - Find ABc, case sensitive                                                               
	                                                                                                    
	  Write these in the readme with but as regex expression with explanations and examples 

