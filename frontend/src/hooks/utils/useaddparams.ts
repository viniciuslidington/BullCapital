import { useSearchParams } from "react-router-dom";

export function useAddParams() {
  const [searchParams, setSearchParams] = useSearchParams();
  return (param: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams);

    if (value === null) {
      newParams.delete(param);
    } else {
      newParams.set(param, value as string);
    }
    setSearchParams(newParams);
  };
}
