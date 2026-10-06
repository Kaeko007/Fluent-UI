local Root = script.Parent
local Themes = require(Root.Themes)
local Flipper = require(Root.Packages.Flipper)

local Creator = {
	Registry = {},
	Signals = {},
	TransparencyMotors = {},
	DefaultProperties = {
		ScreenGui = {
			ResetOnSpawn = false,
			ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
		},
		Frame = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			BorderSizePixel = 0,
		},
		ScrollingFrame = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			ScrollBarImageColor3 = Color3.new(0, 0, 0),
		},
		TextLabel = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			Font = Enum.Font.SourceSans,
			Text = "",
			TextColor3 = Color3.new(0, 0, 0),
			BackgroundTransparency = 1,
			TextSize = 14,
		},
		TextButton = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			AutoButtonColor = false,
			Font = Enum.Font.SourceSans,
			Text = "",
			TextColor3 = Color3.new(0, 0, 0),
			TextSize = 14,
		},
		TextBox = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			ClearTextOnFocus = false,
			Font = Enum.Font.SourceSans,
			Text = "",
			TextColor3 = Color3.new(0, 0, 0),
			TextSize = 14,
		},
		ImageLabel = {
			BackgroundTransparency = 1,
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			BorderSizePixel = 0,
		},
		ImageButton = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			AutoButtonColor = false,
		},
		CanvasGroup = {
			BackgroundColor3 = Color3.new(1, 1, 1),
			BorderColor3 = Color3.new(0, 0, 0),
			BorderSizePixel = 0,
		},
	},
	Font = Font.new("rbxasset://fonts/families/GothamSSm.json"),
}

function Creator.SetFont(FontValue)
	if typeof(FontValue) == "Font" then
		Creator.Font = FontValue
	elseif typeof(FontValue) == "EnumItem" and FontValue.EnumType == Enum.Font then
		Creator.Font = Font.fromEnum(FontValue)
	elseif type(FontValue) == "string" then
		if FontValue:find("rbxasset") or FontValue:find("http") then
			Creator.Font = Font.new(FontValue)
		elseif tonumber(FontValue) then
			Creator.Font = Font.fromId(tonumber(FontValue))
		else
			local Success, EnumFont = pcall(function()
				return Enum.Font[FontValue]
			end)
			if Success and EnumFont then
				Creator.Font = Font.fromEnum(EnumFont)
			else
				Creator.Font = Font.new(FontValue)
			end
		end
	elseif type(FontValue) == "number" then
		Creator.Font = Font.fromId(FontValue)
	end
end

function Creator.GetFont(Weight, Style, CustomFont)
	local BaseFont = CustomFont or Creator.Font
	if typeof(BaseFont) == "EnumItem" then
		BaseFont = Font.fromEnum(BaseFont)
	elseif type(BaseFont) == "string" then
		if BaseFont:find("rbxasset") or BaseFont:find("http") then
			BaseFont = Font.new(BaseFont)
		elseif tonumber(BaseFont) then
			BaseFont = Font.fromId(tonumber(BaseFont))
		else
			local Success, EnumFont = pcall(function()
				return Enum.Font[BaseFont]
			end)
			if Success and EnumFont then
				BaseFont = Font.fromEnum(EnumFont)
			else
				BaseFont = Font.new(BaseFont)
			end
		end
	elseif type(BaseFont) == "number" then
		BaseFont = Font.fromId(BaseFont)
	end

	if typeof(BaseFont) == "Font" then
		return Font.new(BaseFont.Family, Weight or BaseFont.Weight, Style or BaseFont.Style)
	end

	return Font.new("rbxasset://fonts/families/GothamSSm.json", Weight or Enum.FontWeight.Regular, Style or Enum.FontStyle.Normal)
end

function Creator.GetIcon(Name)
	if not Name then
		return nil
	end

	if type(Name) == "number" then
		return "rbxassetid://" .. tostring(Name)
	end

	if type(Name) == "string" then
		if Name == "" then
			return nil
		end
		if Name:find("rbxassetid://") or Name:find("http") then
			return Name
		end

		local Icons = require(Root.Icons).assets
		local CleanName = Name:lower()
		if CleanName:sub(1, 7) == "lucide-" then
			CleanName = CleanName:sub(8)
		end
		CleanName = CleanName:gsub("_", "-")

		if Icons[CleanName] then
			return Icons[CleanName]
		elseif Icons["lucide-" .. CleanName] then
			return Icons["lucide-" .. CleanName]
		end
	end

	return nil
end

local function ApplyCustomProps(Object, Props)
	if Props.ThemeTag then
		Creator.AddThemeObject(Object, Props.ThemeTag)
	end
end

function Creator.AddSignal(Signal, Function)
	table.insert(Creator.Signals, Signal:Connect(Function))
end

function Creator.Disconnect()
	for Idx = #Creator.Signals, 1, -1 do
		local Connection = table.remove(Creator.Signals, Idx)
		Connection:Disconnect()
	end
end

function Creator.GetThemeProperty(Property)
	if Themes[require(Root).Theme][Property] then
		return Themes[require(Root).Theme][Property]
	end
	return Themes["Dark"][Property]
end

function Creator.UpdateTheme()
	for Instance, Object in next, Creator.Registry do
		for Property, ColorIdx in next, Object.Properties do
			Instance[Property] = Creator.GetThemeProperty(ColorIdx)
		end
	end

	for _, Motor in next, Creator.TransparencyMotors do
		Motor:setGoal(Flipper.Instant.new(Creator.GetThemeProperty("ElementTransparency")))
	end
end

function Creator.AddThemeObject(Object, Properties)
	local Idx = #Creator.Registry + 1
	local Data = {
		Object = Object,
		Properties = Properties,
		Idx = Idx,
	}

	Creator.Registry[Object] = Data
	Creator.UpdateTheme()
	return Object
end

function Creator.OverrideTag(Object, Properties)
	Creator.Registry[Object].Properties = Properties
	Creator.UpdateTheme()
end

function Creator.New(Name, Properties, Children)
	local Object = Instance.new(Name)

	-- Default properties
	for Name, Value in next, Creator.DefaultProperties[Name] or {} do
		Object[Name] = Value
	end

	-- Properties
	for Name, Value in next, Properties or {} do
		if Name ~= "ThemeTag" then
			Object[Name] = Value
		end
	end

	-- Children
	for _, Child in next, Children or {} do
		Child.Parent = Object
	end

	ApplyCustomProps(Object, Properties)
	return Object
end

function Creator.SpringMotor(Initial, Instance, Prop, IgnoreDialogCheck, ResetOnThemeChange)
	IgnoreDialogCheck = IgnoreDialogCheck or false
	ResetOnThemeChange = ResetOnThemeChange or false
	local Motor = Flipper.SingleMotor.new(Initial)
	Motor:onStep(function(value)
		Instance[Prop] = value
	end)

	if ResetOnThemeChange then
		table.insert(Creator.TransparencyMotors, Motor)
	end

	local function SetValue(Value, Ignore)
		Ignore = Ignore or false
		if not IgnoreDialogCheck then
			if not Ignore then
				if Prop == "BackgroundTransparency" and require(Root).DialogOpen then
					return
				end
			end
		end
		Motor:setGoal(Flipper.Spring.new(Value, { frequency = 8 }))
	end

	return Motor, SetValue
end

return Creator
