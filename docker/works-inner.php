<?php

$config = parse_ini_file('config.ini', true);
//print_r($config);
$dirHTML = $config['output']['html'];
$dbFileRelative = $config['output']['database'];
//echo $dirHTML;
//echo $dbFilePath;

$dbConnect = new SQLite3($dbFileRelative, SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);

$query = $dbConnect->query("SELECT * FROM works");

while ($row = $query->fetchArray(SQLITE3_ASSOC)) {
  echo '<tr>';
  $chaptNumStr = "<td>";
  foreach ($row as $key => $value) {
    if ($key == "ID") {
      $id = $value;
      echo '<td>'.$value.'</td>';
    } elseif ($key == "title") {
      echo '<td><a href=../'.$dirHTML.'/'.$id.'.html>'.$value.'</a></td>';
    } elseif ($key == "chaptersCount") {
      $chaptNumStr = $chaptNumStr.$value."/";
    } elseif ($key == "chaptersExpected") {
      if ($value == 0) {
        $chaptNumStr = $chaptNumStr."?</td>";
      } else {
        $chaptNumStr = $chaptNumStr.$value."</td>";
      }
    } elseif ($key == "dateLastDownloaded") {
      echo $chaptNumStr;
      echo '<td>'.date("Y/m/d", $value).'</td>';
    }
  }
  echo '</tr>';
}
echo '</table></div>';

?>
