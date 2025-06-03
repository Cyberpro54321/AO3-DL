<?php

function displayChapter($num) {
  global $id;
  echo "<div id='chapter-$num' class='chapter'>";
  echo "<div class='chapter preface group'>";
  echo "<h3 class='title'>Chapter $num: ".file_get_contents("HTML/$id/$num/title.txt")."</h3>";
  if (file_exists("HTML/$id/$num/summary.html")) {
    echo "<div id='summary' class='summary module'>
    <h3 class='heading'>Summary:</h3>
    <blockquote class='userstuff'>";
    echo file_get_contents("HTML/$id/$num/summary.html");
    echo "</blockquote>";
    echo "</div>"; // summary
  }
  if (file_exists("HTML/$id/$num/notes-start.html")) {
    echo "<div id='notes' class='notes module'>
    <h3 class='heading'>Notes:</h3>
    <blockquote class='userstuff'>";
    echo file_get_contents("HTML/$id/$num/notes-start.html");
    echo "</blockquote>";
    echo "</div>"; // notes
  }
  echo "</div>"; // chapter preface group
  
  echo "<div class='userstuff module' role='article'>".file_get_contents("HTML/$id/$num/main.html")."</div>";

  if (file_exists("HTML/$id/$num/notes-end.html")) {
    echo "
    <div class='chapter preface group'>
    <div id='chapter_".$num."_endnotes' class='end notes module'>
    <h3 class='heading'>Notes:</h3>
    <blockquote class='userstuff'>
    ".file_get_contents("HTML/$id/$num/notes-end.html")."
    </blockquote>
    </div>
    </div>
    ";
}

  echo "</div>"; // chapter-num
}

if (array_key_exists("id", $_GET)) {
  $id = $_GET["id"];
}
if (array_key_exists("ch", $_GET)) {
  $chapter = $_GET["ch"]; // Chapter number 0 means show entire work
}

$dbConnect = new SQLite3("main.sqlite", SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);
$q1 = $dbConnect->query("SELECT * FROM works WHERE ID = $id");
$rowWorks = $q1->fetchArray(SQLITE3_ASSOC);
$title = $rowWorks['title'];
$q2 = $dbConnect->query("SELECT * FROM tags WHERE ID = $id");
$rowTags = $q2->fetchArray(SQLITE3_ASSOC);

echo "
<!DOCTYPE html>
<html>
<head>
<title>$title - $id - AO3-DL</title>
<meta charset='UTF-8'>
<link rel='stylesheet' href='normalize.css'>
<link rel='stylesheet' href='custom.css'>
<link rel='icon' href='favicon.png'>
";
$css = array(
  array("01", "-core.css", "screen"),
  array("02", "-elements.css", "screen"),
  array("03", "-region-header.css", "screen"),
  array("04", "-region-dashboard.css", "screen"),
  array("05", "-region-main.css", "screen"),
  array("06", "-region-footer.css", "screen"),
  array("07", "-interactions.css", "screen"),
  array("08", "-actions.css", "screen"),
  array("09", "-roles-states.css", "screen"),
  array("10", "-types-groups.css", "screen"),
  array("11", "-group-listbox.css", "screen"),
  array("12", "-group-meta.css", "screen"),
  array("13", "-group-blurb.css", "screen"),
  array("14", "-group-preface.css", "screen"),
  array("15", "-group-comments.css", "screen"),
  array("16", "-zone-system.css", "screen"),
  array("17", "-zone-home.css", "screen"),
  array("18", "-zone-searchbrowse.css", "screen"),
  array("19", "-zone-tags.css", "screen"),
  array("20", "-zone-translation.css", "screen"),
  array("21", "-userstuff.css", "screen"),
  array("22", "-system-messages.css", "screen"),
  array("25", "-media-midsize.css", "only screen and (max-width: 62em), handheld"),
  array("26", "-media-narrow.css", "only screen and (max-width: 42em), handheld"),
  array("27", "-media-aural.css", "speech"),
  array("28", "-media-print.css", "print"),
);
foreach ($css as $x) {
  echo "<link href='ao3css/$x[0]$x[1]' media='$x[2]' rel='stylesheet' type='text/css'>";
}
unset($css);
echo "<link href='ao3css/sandbox.css' rel='stylesheet'>
<link href='Workskins/$id.css' rel='stylesheet'>
</head>
<body>
<div id='outer' class='wrapper'>
<div id='inner' class='wrapper'>
<div id='main' class='works-show region' role='main'>
";
echo "<div class='wrapper'>".file_get_contents("HTML/$id/tags.html")."</div>";
echo "<div id='workskin'>";
echo "<div class='preface group'>
<h2 class='title heading'>$title</h2>
<h3 class='byline heading'>$rowTags[authorStr]</h3>
";
if ($chapter == 0 or $chapter == 1) {
  if (file_exists("HTML/$id/summary.html")) {
    echo "<div class='summary module'>
      <h3 class='heading'>Summary:</h3>
      <blockquote class='userstuff'>
      ".file_get_contents("HTML/$id/summary.html")."</blockquote></div>";
  }
  if (file_exists("HTML/$id/notes.html")) {
    echo "<div class='notes module'>
      <h3 class='heading'>Notes:</h3>
      <blockquote class='userstuff'>
      ".file_get_contents("HTML/$id/notes.html")."</blockquote></div>";
  }
}
echo "</div>"; // preface group

echo "<div id='chapters' role='article'>";
if ($chapter == 0) {
  for ($i = 1; $i <= $rowWorks['chaptersCount']; $i++) { 
    displayChapter($i);
  }
} else {
  displayChapter($chapter);
}

echo "
</div>
</div>
</div>
</div>
</div>
</body>
</html>
"; // outer, inner, main, workskin, chapters
?>
