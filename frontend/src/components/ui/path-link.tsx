import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { useLocation, useNavigate } from "react-router-dom";
import { capitalizeFirstLetter } from "@/lib/utils";

export function PathLink() {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <Breadcrumb>
      <BreadcrumbList className="text-primary/70 text-base font-medium">
        <BreadcrumbItem>
          <BreadcrumbLink
            className="hover:text-primary cursor-pointer"
            onClick={() => navigate("/")}
          >
            Home
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        {location.state?.from && (
          <>
            <BreadcrumbItem>
              <BreadcrumbLink
                className="cursor-pointer"
                onClick={() => navigate(-1)}
              >
                {capitalizeFirstLetter(location.state.from)}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
          </>
        )}
        <BreadcrumbItem>
          <BreadcrumbPage className="text-primary cursor-pointer font-medium">
            {capitalizeFirstLetter(location.pathname.replace("/", ""))}
          </BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  );
}
