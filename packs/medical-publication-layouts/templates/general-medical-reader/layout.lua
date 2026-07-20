-- MAS Scholar Skills general-medical-reader.v1
-- Generic Pandoc layout behavior. No study, table, figure, or panel ids belong here.

local top_level_section_seen = false

local function is_latex()
  return FORMAT == "latex" or FORMAT == "beamer"
end

function Header(header)
  if not is_latex() or header.level ~= 1 then
    return nil
  end
  if top_level_section_seen then
    return {
      pandoc.RawBlock("latex", "\\FloatBarrier"),
      header,
    }
  end
  top_level_section_seen = true
  return nil
end

function Image(image)
  if is_latex() and image.attributes.width == nil then
    image.attributes.width = "94%"
    return image
  end
  return nil
end

function Pandoc(document)
  if is_latex() then
    table.insert(document.blocks, pandoc.RawBlock("latex", "\\FloatBarrier"))
  end
  return document
end
