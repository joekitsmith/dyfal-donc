import TextField from "@mui/material/TextField";

type CourseSearchBoxProps = {
  readonly onChange: (value: string) => void;
  readonly value: string;
};

export function CourseSearchBox({ onChange, value }: CourseSearchBoxProps) {
  return (
    <TextField
      fullWidth
      label="Search words and phrases"
      onChange={(event) => {
        onChange(event.target.value);
      }}
      type="search"
      value={value}
    />
  );
}
