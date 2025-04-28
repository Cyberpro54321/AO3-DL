<?php

function getOption($input, $option){
  if (($input & pow(2, $option)) == pow(2, $option)) {
    return 1;
  } else {
    return 0;
  }
}

$config = parse_ini_file('config.ini', true);
//print_r($config);
$dirHTML = $config['output']['html'];
$dbFileRelative = $config['output']['database'];
//echo $dirHTML;
//echo $dbFilePath;

$dbConnect = new SQLite3($dbFileRelative, SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);

$query = $dbConnect->query("SELECT * FROM works");

while ($row = $query->fetchArray(SQLITE3_ASSOC)) {
  $chaptNumStr = "";
  $reqTagRat = "";
  $reqTagCat = "";
  $tagsFan = "";
  $tagsMain = "";
  foreach ($row as $key => $value) {
    if ($key == "ID") {
      $id = str_pad($value, 8, '0', STR_PAD_LEFT);;
      $q2 = $dbConnect->query("SELECT * FROM tags WHERE ID=$value");
      $r2 = $q2->fetchArray(SQLITE3_ASSOC);
    } elseif ($key == "title") {
      $link = '<a href=../'.$dirHTML.'/'.$id.'.html>'.$value.'</a>';
    } elseif ($key == "chaptersCount") {
      $chaptNumStr = $chaptNumStr.$value."/";
      $chaptCount = $value;
    } elseif ($key == "chaptersExpected") {
      if ($value == 0) {
        $chaptNumStr = $chaptNumStr."?";
        $reqTagCmp = "<td class='tagIncomplete'>N</td>";
      } else {
        $chaptNumStr = $chaptNumStr.$value;
        if ($value == $chaptCount) {
          $reqTagCmp = "<td class='tagComplete'>Y</td>";
        } else {
          $reqTagCmp = "<td class='tagIncomplete'>N</td>";
        }
      }
    } elseif ($key == "dateLastDownloaded") {
      $dateDL = date("Y/m/d", $value);
    } elseif ($key == "dateLastEdited") {
      $dateEd = date("Y/m/d", $value);
    } elseif ($key == "dateLastUpdated") {
      $dateUp = date("Y/m/d", $value);
    }
  }
  foreach ($r2 as $key => $value) {
    if ($key == "rating") {
      if ($value == 1) {
        $reqTagRat = "<td class='ratingN'> </td>";
      } elseif ($value == 2) {
        $reqTagRat = "<td class='ratingG'>G</td>";
      } elseif ($value == 3) {
        $reqTagRat = "<td class='ratingT'>T</td>";
      } elseif ($value == 4) {
        $reqTagRat = "<td class='ratingM'>M</td>";
      } elseif ($value == 5) {
        $reqTagRat = "<td class='ratingE'>E</td>";
      }
    } elseif ($key == "category") {
      if ($value == 0) {
        $reqTagCat = "<td class='catN'> </td>";
      } elseif ($value == 1) {
        $reqTagCat = "<td class='catFF'>♀</td>";
      } elseif ($value == 2) {
        $reqTagCat = "<td class='catFM'>/</td>";
      } elseif ($value == 4) {
        $reqTagCat = "<td class='catG'>o</td>";
      } elseif ($value == 8) {
        $reqTagCat = "<td class='catMM'>♂</td>";
      } elseif ($value == 32) {
        $reqTagCat = "<td class='catO'>?</td>";
      } else {
        $reqTagCat = "<td class='catMu'>!</td>";
      }
    } elseif ($key == "warnings") {
      $rtw = 0;
      $warnStr = "";
      if (getOption($value, 5) == 1) {
        $warnStr = "Creator Chose Not To Use Archive Warnings";
        $rtw = max(3, $rtw);
      } elseif (getOption($value, 4) == 1) {
        $warnStr = "Underage";
        $rtw = max(2, $rtw);
      } elseif (getOption($value, 3) == 1) {
        $warnStr = "Rape/Non-Con";
        $rtw = max(2, $rtw);
      } elseif (getOption($value, 2) == 1) {
        $warnStr = "Major Character Death";
        $rtw = max(2, $rtw);
      } elseif (getOption($value, 1) == 1) {
        $warnStr = "Graphic Depictions Of Violence";
        $rtw = max(2, $rtw);
      } elseif (getOption($value, 0) == 1) {
        $warnStr = "No Archive Warnings Apply";
        $rtw = max(1, $rtw);
      }
      $tagsMain .= "<li class='tagWarn'><a>$warnStr</a></li>";
      if ($rtw == 3) {
        $reqTagWrn = "<td class='warning6'>?</td>";
      } elseif ($rtw == 2) {
        $reqTagWrn = "<td class='warningX'>!</td>";
      } elseif ($rtw == 1) {
        $reqTagWrn = "<td class='warning1'> </td>";
      }
    } elseif (substr($key, 0, 5) == "tagFa") {
      if (strlen($value) != 0) {
        $tagsFan .= "<li class='tagFan'><a>$value</a></li>";
      }
    } elseif (substr($key, 0, 4) == "tagS") {
      if (strlen($value) != 0) {
        $tagsMain .= "<li class='tagShips'><a>$value</a></li>";
      }
    } elseif (substr($key, 0, 4) == "tagC") {
      if (strlen($value) != 0) {
        $tagsMain .= "<li class='tagChar'><a>$value</a></li>";
      }
    } elseif (substr($key, 0, 5) == "tagFr") {
      if (strlen($value) != 0) {
        $tagsMain .= "<li class='tagFreeform'><a>$value</a></li>";
      }
    }
  }
  echo '<li>';
  echo '<div class="header">';
  echo '<table class="requiredTags"><tr>'.$reqTagRat.$reqTagCat.'</tr><tr>'.$reqTagWrn.$reqTagCmp.'</tr></table>';
  echo '<div>';
  echo '<h4>'.$link." (".$id.')</h4>'; # TODO: List authors on this page
  echo "<h5><ul class='tags fandoms'>$tagsFan</ul></h5>";
  echo '</div>';
  echo '<div>';
  echo '<p class="timestamp">Date Updated: '.$dateUp.'</p>';
  echo '<p class="timestamp">Date Edited: '.$dateEd.'</p>';
  echo '<p class="timestamp">Date Downloaded: '.$dateDL.'</p>';
  echo '</div>';
  echo '</div>';
  echo "<ul class='tags mainTags'>$tagsMain</ul>";
  echo "<div class='stats'>Chapters: $chaptNumStr</div>";
  echo '</li>';
  // print_r($r2);
}

?>
