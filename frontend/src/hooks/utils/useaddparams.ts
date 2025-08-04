import { useSearchParams } from "react-router-dom";

export function useAddParams() {
  const [searchParams, setSearchParams] = useSearchParams();
  return (param: string, value: string) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set(param, value);
    setSearchParams(newParams);
  };
}
