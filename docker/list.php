<?php

define("TAG_CATEGORIES", array(
  array("Fandom", "tagFan"),
  array("Ship", "tagShips"),
  array("Character", "tagChar"),
  array("Freeform", "tagFreeform")
));

function intToArray($input) {
  $array = [];
  for ($i=7; $i >= 0; $i--) { 
    $j = pow(2, $i);
    if (($input & $j) == $j) {
      $k = 1;
      $input -= $j;
    } else {
      $k = 0;
    }
    $array[$i] = $k;
  }
  return $array;
}
function rowToHtmlSimple($row) {
  global $dirHTML;
  $id = str_pad($row['ID'], 8, '0', STR_PAD_LEFT);
  $titleLink = "<td><a href=$dirHTML/$id.html>".$row['title']."</a></td>";
  $chp1 = $row['chaptersCount'];
  $chp2 = $row['chaptersExpected'];
  if ($chp2 == 0) {
    $chp2 = "?";
  }
  $dateDL = date("Y/m/d", $row['dateLastDownloaded']);
  return "<tr><td>$id</td>$titleLink<td>$chp1/$chp2</td><td>$dateDL</td></tr>";
}
function rowToHtmlTags($row) {
  global $dirHTML, $dbConnect;
  $id = str_pad($row['ID'], 8, '0', STR_PAD_LEFT);
  $titleLink = "<a href=$dirHTML/$id.html>".$row['title']."</a>";
  $chp1 = $row['chaptersCount'];
  $chp2 = $row['chaptersExpected'];
  if ($chp2 == 0) {
    $chp2 = "?";
    $reqTagCmp = "<td class='tagIncomplete'>N</td>";
  } else {
    if ($chp2 == $chp1) {
      $reqTagCmp = "<td class='tagComplete'>Y</td>";
    } else {
      $reqTagCmp = "<td class='tagIncomplete'>N</td>";
    }
  }
  if ($row['dateLastDownloaded'] == 0) {
    $dateDL = "Unknown";
  } else {
    $dateDL = date("Y/m/d", $row['dateLastDownloaded']);
  }
  if ($row['dateLastEdited'] == 0) {
    $dateEd = "Unknown";
  } else {
    $dateEd = date("Y/m/d", $row['dateLastEdited']);
  }
  $dateUp = date("Y/m/d", $row['dateLastUpdated']);
  $q2 = $dbConnect->query("SELECT * FROM tags WHERE ID=$id");
  $r2 = $q2->fetchArray(SQLITE3_ASSOC);
  switch ($r2['rating']) {
    case 1:
      $reqTagRat = "<td class='ratingN'> </td>";
      break;
    case 2:
      $reqTagRat = "<td class='ratingG'>G</td>";
      break;
    case 3:
      $reqTagRat = "<td class='ratingT'>T</td>";
      break;
    case 4:
      $reqTagRat = "<td class='ratingM'>M</td>";
      break;
    case 5:
      $reqTagRat = "<td class='ratingE'>E</td>";
      break;
    default:
      $reqTagRat = "";
  }
  switch ($r2['category']) {
    case 0:
      $reqTagCat = "<td class='catN'> </td>";
      break;
    case 1:
      $reqTagCat = "<td class='catFF'>♀</td>";
      break;
    case 2:
      $reqTagCat = "<td class='catFM'>/</td>";
      break;
    case 4:
      $reqTagCat = "<td class='catG'>o</td>";
      break;
    case 8:
      $reqTagCat = "<td class='catMM'>♂</td>";
      break;
    case 32:
      $reqTagCat = "<td class='catO'>?</td>";
      break;
    default:
      $reqTagCat = "<td class='catMu'>!</td>";
  }
  $rtw = 0;
  $warnArray = [];
  foreach (intToArray($r2['warnings']) as $key => $value) {
    if ($value == 1) {
      switch ($key) {
        case 0:
          $warnArray[] = "No Archive Warnings Apply";
          $rtw = max(1, $rtw);
          break;
        case 1:
          $warnArray[] = "Graphic Depictions Of Violence";
          $rtw = max(2, $rtw);
          break;
        case 2:
          $warnArray[] = "Major Character Death";
          $rtw = max(2, $rtw);
          break;
        case 3:
          $warnArray[] = "Rape/Non-Con";
          $rtw = max(2, $rtw);
          break;
        case 4:
          $warnArray[] = "Underage";
          $rtw = max(2, $rtw);
          break;
        case 5:
          $warnArray[] = "Creator Chose Not To Use Archive Warnings";
          $rtw = max(3, $rtw);
      }
    }
  }
  $tagsMain = "";
  $tagsFan = "";
  foreach ($warnArray as $value) {
    $tagsMain .= "<li class='tagWarn'><a>$value</a></li>";
  }
  switch ($rtw) {
    case 3:
      $reqTagWrn = "<td class='warning6'>?</td>";
      break;
    case 2:
      $reqTagWrn = "<td class='warningX'>!</td>";
      break;
    case 1:
      $reqTagWrn = "<td class='warning1'> </td>";
      break;
  }
  $authorStr = $r2['authorStr'];
  $summaryStr = file_get_contents("$id/summary.html");
  foreach (TAG_CATEGORIES as $value) {
    for ($i=1; $i <= 75; $i++) { 
      $j = $r2["tag$value[0]$i"];
      if (strlen($j) != 0) {
        if ($value == TAG_CATEGORIES[0]) {
          $tagsFan .= "<li class='$value[1]'><a>$j</a></li>";
        } else {
          $tagsMain .= "<li class='$value[1]'><a>$j</a></li>";
        }
      }
    }
  }
  return "<li>
    <div class='header'>
    <table class='requiredTags'>
    <tr>$reqTagRat$reqTagCat</tr><tr>$reqTagWrn$reqTagCmp</tr>
    </table>
    <div>
    <h4>$titleLink ($id) by $authorStr</h4>
    <h5><ul class='tags fandoms'>$tagsFan</ul></h5>
    </div>
    <div>
    <p class='timestamp'>Date Updated: $dateUp</p>
    <p class='timestamp'>Date Edited: $dateEd</p>
    <p class='timestamp'>Date Downloaded: $dateDL</p>
    </div>
    </div>
    <ul class='tags mainTags'>$tagsMain</ul>
    <blockquote>$summaryStr</blockquote>
    <div class='stats'>Chapters: $chp1/$chp2</div>
    </li>";
}

# 0 = simple
# 1 = tags
$mode = 1;

# 0 = all works
# 1 = all works in certain series
$target = 0;

# by default, unused
# if $target = 1, this represents the series ID to view the works of
$subject = -1;

if (array_key_exists("mode", $_GET)) {
  switch (strtolower($_GET['mode'])) {
    case "simple":
    case "0":
    case 0:
      $mode = 0;
      break;
    case "tags":
    case "1":
    case 1:
      $mode = 1;
      break;
  }
}
if (array_key_exists("target", $_GET)) {
  switch (strtolower($_GET['target'])) {
    case 'all':
    case "0":
    case 0:
      $target = 0;
      break;
    case 'series':
    case "1":
    case 1:
      $target = 1;
      break;
  }
}
if (array_key_exists("subject", $_GET)) {
  $subject = $_GET['subject'];
}
// echo "<li>$mode, $target, $subject</li>";

$config = parse_ini_file('config.ini', true);
//print_r($config);
$dirHTML = $config['output']['html'];
$dbFileRelative = $config['output']['database'];
//echo $dirHTML;
//echo $dbFilePath;

$dbConnect = new SQLite3($dbFileRelative, SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);

switch ($target) {
  // case 1:
  
  case 0:
  default:
    $query = $dbConnect->query("SELECT * FROM works");
    $pageTitleCore = "Browse All Downloaded Works"; 
    break;
}

switch ($mode) {
  case 0:
    $pageTitleCore .= " - Simple Mode";
    break;
  case 1:
    $pageTitleCore .= " - Tags Mode";
    break;
}

echo "
<!DOCTYPE html>
<html>
  <head>
    <title>$pageTitleCore - AO3-DL</title>
    <meta charset='UTF-8'>
    <link rel='stylesheet' href='normalize.css'>
    <link rel='stylesheet' href='list.css'>
    <link rel='stylesheet' href='custom.css'>
    <link rel='icon' href='favicon.png'>
  </head>
  <body>
";
switch ($mode) {
  case 0:
    echo "<table class='workList'>
        <tr>
          <th class='tableColId'>ID</th>
          <th class='tableColTitle'>Title</th>
          <th class='tableColChapters'>Chapters</th>
          <th class='tableColDateDL'>Date Downloaded</th>
        </tr>
    ";
    break;
  case 1:
    echo "<ul class='workList'>";
    break;
}
while ($row = $query->fetchArray(SQLITE3_ASSOC)) {
  switch ($mode) {
    case 0:
      echo rowToHtmlSimple($row);
      break;
    case 1:
      echo rowToHtmlTags($row);
      break;
  }
}
switch ($mode) {
  case 0:
    echo "</table>";
    break;
  case 1:
    echo "</ul>";
    break;
}

echo "
</body>
</html>
";

?>
