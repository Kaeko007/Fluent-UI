import os

SRC_DIR = r"C:\Users\devtu\Desktop\Fluent-master\src"
OUTPUT_FILE = r"C:\Users\devtu\Desktop\Fluent-master\main.lua"

modules = {}
dirs_set = set()

for root, dirs, files in os.walk(SRC_DIR):
    for f in files:
        if f.endswith(".lua") and not f.endswith(".spec.lua"):
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, SRC_DIR).replace("\\", "/")
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            modules[rel_path] = content

            dir_parts = rel_path.split("/")[:-1]
            cur = ""
            for p in dir_parts:
                cur = f"{cur}/{p}" if cur else p
                dirs_set.add(cur)

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

nodes = {}
nodes[""] = "Root"
nodes["init.lua"] = "Root"

var_map = {} # string -> unique var
var_counter = 1

def get_unique_var(prefix):
    global var_counter
    v = f"{prefix}_{var_counter}"
    var_counter += 1
    return v

# Create directory nodes first
sorted_dirs = sorted(list(dirs_set), key=lambda d: (d.count("/"), d))
for d in sorted_dirs:
    parts = d.split("/")
    folder_name = parts[-1]
    parent_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
    parent_var = nodes[parent_dir]
    
    init_path = f"{d}/init.lua"
    if init_path in modules:
        var_name = get_unique_var(f"mod_{folder_name}")
        nodes[d] = var_name
        nodes[init_path] = var_name
        lua_code.append(f'local {var_name} = MakeVirtualInstance("ModuleScript", "{folder_name}", {parent_var})')
    else:
        var_name = get_unique_var(f"dir_{folder_name}")
        nodes[d] = var_name
        lua_code.append(f'local {var_name} = MakeVirtualInstance("Folder", "{folder_name}", {parent_var})')

# Create file nodes
for rel_path in sorted(list(modules.keys()), key=lambda p: (p.count("/"), p)):
    if rel_path == "init.lua" or rel_path in nodes:
        continue
    parts = rel_path.split("/")
    file_name = parts[-1].replace(".lua", "")
    parent_dir = "/".join(parts[:-1]) if len(parts) > 1 else ""
    parent_var = nodes[parent_dir]
    
    var_name = get_unique_var(f"file_{file_name}")
    nodes[rel_path] = var_name
    lua_code.append(f'local {var_name} = MakeVirtualInstance("ModuleScript", "{file_name}", {parent_var})')

lua_code.append("\n-- Module Implementation Bindings")

for rel_path, code in modules.items():
    var_name = nodes[rel_path]
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

print(f"Fixed bundle created at {OUTPUT_FILE} ({len(bundle_content)} bytes)")
