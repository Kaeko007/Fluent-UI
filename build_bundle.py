import os
import re

SRC_DIR = r"C:\Users\devtu\Desktop\Fluent-master\src"
OUTPUT_FILE = r"C:\Users\devtu\Desktop\Fluent-master\main.lua"

def get_tree_structure(src_dir):
    modules = {} # rel_path_without_ext -> code
    for root, dirs, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".lua") and not f.endswith(".spec.lua"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, src_dir).replace("\\", "/")
                with open(full_path, "r", encoding="utf-8") as file:
                    content = file.read()
                modules[rel_path] = content
    return modules

modules = get_tree_structure(SRC_DIR)

# Generate Lua Virtual File System Code
lua_code = []
lua_code.append("""--[[
    Fluent Interface Suite (Standalone Bundle)
    Custom Font & Lucide Icon Enhanced
--]]

local VirtualModules = {}
local Cache = {}

local function MakeVirtualInstance(className, name, parent)
    local children = {}
    local childrenList = {}
    local inst = newproxy(true)
    local meta = getmetatable(inst)
    
    meta.__index = function(self, key)
        if key == "Name" then return name
        elseif key == "ClassName" then return className
        elseif key == "Parent" then return parent
        elseif key == "GetChildren" then
            return function() return childrenList end
        elseif key == "FindFirstChild" then
            return function(self, childName) return children[childName] end
        elseif children[key] then
            return children[key]
        end
        error("'" .. tostring(key) .. "' is not a valid member of " .. name, 2)
    end
    
    meta.__tostring = function() return name end
    
    if parent then
        local pMeta = getmetatable(parent)
        pMeta._registerChild(name, inst)
    end
    
    meta._registerChild = function(childName, childInst)
        children[childName] = childInst
        table.insert(childrenList, childInst)
    end
    
    return inst
end

local RealRequire = require
local ModuleFunctions = {}

local function customRequire(target)
    if typeof(target) == "Instance" or type(target) == "userdata" then
        if Cache[target] then
            return Cache[target]
        end
        local func = ModuleFunctions[target]
        if func then
            local result = func()
            Cache[target] = result
            return result
        end
    end
    return RealRequire(target)
end

local Root = MakeVirtualInstance("ModuleScript", "Fluent", nil)
""")

# Order files so parents exist before children
paths = sorted(modules.keys(), key=lambda p: (p.count("/"), p))

# Create Virtual Nodes
nodes = {} # rel_path -> node_var_name
nodes["init.lua"] = "Root"

var_counter = 1
for rel in paths:
    if rel == "init.lua":
        continue
    parts = rel.split("/")
    var_name = f"node_{var_counter}"
    var_counter += 1
    nodes[rel] = var_name
    
    # Determine parent and node name
    if len(parts) == 1:
        # direct child of Root
        parent_var = "Root"
        node_name = parts[0].replace(".lua", "")
    else:
        # nested
        filename = parts[-1]
        if filename == "init.lua":
            # Parent is parent of parent dir
            parent_dir = "/".join(parts[:-2])
            parent_var = nodes.get(parent_dir + "/init.lua", "Root") if parent_dir else "Root"
            node_name = parts[-2]
        else:
            parent_dir = "/".join(parts[:-1])
            parent_var = nodes.get(parent_dir + "/init.lua", nodes.get(parent_dir, "Root"))
            node_name = filename.replace(".lua", "")
            
    lua_code.append(f'local {var_name} = MakeVirtualInstance("ModuleScript", "{node_name}", {parent_var})')

lua_code.append("\n-- Module Implementation Bindings")

for rel in paths:
    var_name = nodes[rel]
    code = modules[rel]
    
    # We set environment for closure or pass require
    lua_code.append(f"ModuleFunctions[{var_name}] = function()")
    lua_code.append(f"    local script = {var_name}")
    lua_code.append("    local require = customRequire")
    lua_code.append(code)
    lua_code.append("end\n")

lua_code.append("""
local Library = customRequire(Root)
return Library
""")

bundle_content = "\n".join(lua_code)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(bundle_content)

print(f"Bundle created successfully at {OUTPUT_FILE} ({len(bundle_content)} bytes)")
