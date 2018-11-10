<div style="position:absolute;
					    top:50%;
					    right:0;
					    left:45%;">
<form action="/" method="get">
	<input type="text" name="keywords">
	<input type="submit" name="submit" value="submit">
</form>

<strong>results:</strong>
<table id="results">
%for keyword in results:
	<tr>
		<td>{{keyword}}</td>
		<td>{{results[keyword]}}</td>
	</tr>
%end
</table>

<strong>history:</strong>
<table id="history">
%for keyword in history:
	<tr>
		<td>{{keyword[0]}}</td>
		<td>{{keyword[1]}}</td>
	</tr>
%end
</table>
