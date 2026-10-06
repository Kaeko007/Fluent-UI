local Root = script.Parent.Parent
local Components = Root.Components
local Flipper = require(Root.Packages.Flipper)
local Creator = require(Root.Creator)

local Paragraph = {}
Paragraph.__index = Paragraph
Paragraph.__type = "Paragraph"

function Paragraph:New(Config)
	assert(Config.Title, "Paragraph - Missing Title")
	Config.Content = Config.Content or ""

	local ParagraphFrame = require(Components.Element)(Config.Title, Config.Content, self.Container or Paragraph.Container, false, Config.Icon)
	ParagraphFrame.Frame.BackgroundTransparency = 0.92
	ParagraphFrame.Border.Transparency = 0.6

	return ParagraphFrame
end

return Paragraph
